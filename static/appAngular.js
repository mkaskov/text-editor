function $id(id) {
  return document.getElementById(id);
}

var app = angular.module("dlte", ["ngRoute","cgBusy","ngScrollbar"])
.config(function ($routeProvider, $locationProvider,$interpolateProvider) {
	 $interpolateProvider.startSymbol('{[');
     $interpolateProvider.endSymbol(']}');
	
    $routeProvider
	.when("/doc", {
        templateUrl: "static/template/main.html",
        controller: "mainController"
    })
	.when("/demo", {
        templateUrl: "static/template/demo.html",
        controller: "demoController"
    })
	.when("/dataprepare", {
        templateUrl: "static/template/dataPrepare.html",
        controller: "dataPrepareController"
    })
	.otherwise({
        redirectto: '/doc'
    });
})
.factory("rsService", ["$http", "$q", function ($http, $q) {
	var obj = {};
	
	    obj.convertString = function (inputString) {
            return $http({
                method: 'POST',
                url: "/decode_sentense",
                data: JSON.stringify({"query":inputString}),
                headers: {
                    'Content-type': "application/json; charset=utf-8"
                },
            })
            .success(function (data) {
			})
            .error(function (data) {
            });
        };
		
		obj.convertArray = function (inputArray) {
            return $http({
                method: 'POST',
                url: "/decode",
                data: JSON.stringify(inputArray),
                headers: {
                    'Content-type': "application/json; charset=utf-8"
                },
            })
            .success(function (data) {
			})
            .error(function (data) {
            });
        };

	return obj;
}])
.factory("appService", ["$http", "$q", function ($http, $q) {var obj = {selector:"main"};return obj;}])
.controller("appController", function ($rootScope, $scope,appService,$location) {
	
    $scope.getSelector = function () {
        return appService.selector;
    };
    $scope.setSelector = function (e) {
        appService.selector = e;
    };
	
	$scope.onLoad = function (){
		 if($location.path().substr(1).length===0){
			 $location.path("/doc");
			  $scope.setSelector("doc");
		 }else{
			  $scope.setSelector($location.path().substr(1));
		 }
	}
	$scope.onLoad ();
})
.controller("mainController", function ($scope,rsService,appService,$timeout) {
	$scope.reader = new FileReader();
	$scope.fileContent = [];
	$scope.fileHeadind = {};
	
	$scope.reader.onload = function(aEvent) {
		$scope.fileContent = docx(btoa(aEvent.target.result));
		$scope.fileHeadind = $scope.fileContent[0];
		$scope.fileContent.splice(0, 1);
		
		// for(var i=0;i<$scope.fileContent.length;i++){
			// // var result = $scope.fileContent[i].col3.split(/[\\.!\?]/); 
			// var result = $scope.fileContent[i].col3.split(/[\.!\?\r\f]\s|[\r\f]/); //увы в получаемом тексте уже не может быть знаков перевода строки или переноса страницы
			// $scope.fileContent[i].data = [];
			// for(var z=0;z<result.length;z++){
				// if(result[z].trim().length>0)
				// $scope.fileContent[i].data.push({input:result[z].trim(),out:""});
			// }
		
		// }
		
		window.console.log($scope.fileContent);
		appService.DocFileContent = $scope.fileContent;
		appService.DocFileHeadind = $scope.fileHeadind;
		
		$scope.$apply(function () {});
	};
	
	 $scope.loadDocument = function () {
		$scope.reader.readAsBinaryString($id('file').files[0]);
	 };	 
	
	$scope.convertDoc = function (){
		$scope.myPromise = rsService.convertArray($scope.fileContent).then(function (data) {
				for(var i=0;i<data.data.answer.length;i++){
					var tmpItem = data.data.answer[i].out;
					for(var z=0;z<tmpItem.length;z++){
						$scope.fileContent[i].data[z].out=tmpItem[z];
					}
				}			
		});			
	};
	
	$scope.removeRow = function(pIndex,sIndex){
		$scope.fileContent[pIndex].data.splice(sIndex, 1);
		
	}
	
	$scope.mergeRow = function(pIndex,sIndex){
		$scope.fileContent[pIndex].data[sIndex].input=($scope.fileContent[pIndex].data[sIndex].input+ " "+ $scope.fileContent[pIndex].data[sIndex+1].input).trim();
		$scope.fileContent[pIndex].data[sIndex].out=($scope.fileContent[pIndex].data[sIndex].out +" " + $scope.fileContent[pIndex].data[sIndex+1].out).trim();
		$scope.fileContent[pIndex].data.splice(sIndex+1, 1);
	}
	
	$scope.onLoad = function (){
		if(appService.DocFileContent)
		  $scope.fileContent = appService.DocFileContent;
		if(appService.DocFileHeadind)
   	      $scope.fileHeadind = appService.DocFileHeadind;
	}
	$scope.onLoad ();
	 
})
.controller("demoController", function ($scope,rsService,$timeout,appService) {
	$scope.textObj ={areaText1:"",areaText2:""};

    $scope.convertText = function (selector) {
        switch (selector){
			case 1:
				$scope.textObj.areaText1 = "Содержание зерен крупностью свыше десяти миллиметров не должно превышать пять процентов по массе."			
			break;
			case 2:
				$scope.textObj.areaText1 = "Листы гипсокартонные или эквивалент. Отклонение от прямоугольности не должно быть более 6 мм."
			break;
		};
		$scope.myPromise = rsService.convertString($scope.textObj.areaText1).then(function (data) {
            $scope.textObj.areaText2 =  data.data.answer;  
			appService.DemoTextObj = $scope.textObj;
        });
    };
	
	$scope.onLoad = function (){
		if(appService.DemoTextObj)
		  $scope.textObj = appService.DemoTextObj;
	}
	$scope.onLoad ();
	
})
.controller("dataPrepareController", function ($scope,rsService,appService,$timeout) {
	$scope.reader = new FileReader();
	$scope.fileContent = [];
	$scope.fileHeadind = {};
	$scope.fileContentLearn = [];
	
	$scope.selectedFile = "";
	
	
	$scope.combineFiles = function (){
		if($scope.fileContent.length==0 || $scope.fileContentLearn.length==0)
			return;
		
		for(var i in $scope.fileContent){
			var elem = $scope.fileContent[i].data;
			for(var y in elem){
				var elemY = elem[y];
				if($scope.fileContentLearn[i].data[y])
					elemY.out = $scope.fileContentLearn[i].data[y].input;
			}
			if(elem.length<$scope.fileContentLearn[i].data.length){
				
				for(var y=elem.length;y<$scope.fileContentLearn[i].data.length;y++){
					elem.push({input:"",out:$scope.fileContentLearn[i].data[y].input});
				}
			}
		}
		
	    appService.LearnFileContent = $scope.fileContent;
	}
	
	$scope.reader.onload = function(aEvent) {
		switch($scope.selectedFile){
				case "file":
					$scope.fileContent = docx(btoa(aEvent.target.result));
					$scope.fileHeadind = $scope.fileContent[0];
					$scope.fileContent.splice(0, 1);
				break;
				case "fileTrain":
					$scope.fileContentLearn = docx(btoa(aEvent.target.result));
					$scope.fileContentLearn.splice(0, 1);
				break;
		}
		
		$scope.combineFiles();
			
		appService.LearnFileContent = $scope.fileContent;
		appService.LearnFileHeadind = $scope.fileHeadind;
		appService.LearnfileContentLearn = $scope.fileContentLearn;
		
		$scope.$apply(function () {});
	};
	
	 $scope.loadDocument = function (fileName) {
		$scope.selectedFile = fileName;
		$scope.reader.readAsBinaryString($id(fileName).files[0]);
	 };	 
	 
	$scope.mergeRow = function(type,pIndex,sIndex){
		if($scope.fileContent[pIndex].data[sIndex+1]){
			switch(type){
				case "input":
					$scope.fileContent[pIndex].data[sIndex].input=($scope.fileContent[pIndex].data[sIndex].input+ " "+ $scope.fileContent[pIndex].data[sIndex+1].input).trim();
					for(var i=sIndex+1;i<$scope.fileContent[pIndex].data.length;i++){
						if($scope.fileContent[pIndex].data[i+1]){
							$scope.fileContent[pIndex].data[i].input=$scope.fileContent[pIndex].data[i+1].input;
							$scope.fileContent[pIndex].data[i+1].input="";
						}else{
							$scope.fileContent[pIndex].data[i].input = "";
						}
					}
				break;
				case "train":
					$scope.fileContent[pIndex].data[sIndex].out=($scope.fileContent[pIndex].data[sIndex].out+ " "+ $scope.fileContent[pIndex].data[sIndex+1].out).trim();
					for(var i=sIndex+1;i<$scope.fileContent[pIndex].data.length;i++){
						if($scope.fileContent[pIndex].data[i+1]){
							$scope.fileContent[pIndex].data[i].out=$scope.fileContent[pIndex].data[i+1].out;
							$scope.fileContent[pIndex].data[i+1].out="";
						}else{
							$scope.fileContent[pIndex].data[i].out = "";
						}
					}	
				break;
			}
		}	
		
		var lInp = $scope.fileContent[pIndex].data[$scope.fileContent[pIndex].data.length-1].input.trim().length;
		var lOut = $scope.fileContent[pIndex].data[$scope.fileContent[pIndex].data.length-1].out.trim().length;
		if(lInp ==0 && lOut ==0){
			$scope.fileContent[pIndex].data.splice(-1,1);
		}
	}
	
	$scope.onLoad = function (){
		if(appService.LearnFileContent)
		  $scope.fileContent = appService.LearnFileContent;
		if(appService.LearnFileHeadind)
   	      $scope.fileHeadind = appService.LearnFileHeadind;
		if(appService.DocFileHeadind)
			$scope.fileContentLearn = appService.LearnfileContentLearn; 
	}
	$scope.onLoad ();
	 
});