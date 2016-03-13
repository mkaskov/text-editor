# Description:
# Example neural editor models.

package(default_visibility = ["//visibility:public"])

licenses(["notice"])  # what license???

exports_files(["LICENSE"])

py_library(
    name = "package",
    srcs = [
        "__init__.py",
    ],
    srcs_version = "PY2AND3",
    deps = [
        ":data_utils",
        ":seq2seq_model",
    ],
)

py_library(
    name = "data_utils",
    srcs = [
        "data_utils.py",
    ],
    srcs_version = "PY2AND3",
    deps = ["//tensorflow:tensorflow_py"],
)

py_library(
    name = "seq2seq_model",
    srcs = [
        "seq2seq_model.py",
    ],
    srcs_version = "PY2AND3",
    deps = [
        ":data_utils",
        "//tensorflow:tensorflow_py",
        "//tensorflow/models/rnn:seq2seq",
    ],
)

py_binary(
    name = "editor",
    srcs = [
        "editor.py",
    ],
    srcs_version = "PY2AND3",
    deps = [
        ":data_utils",
        ":seq2seq_model",
        "//tensorflow:tensorflow_py",
    ],
)

py_test(
    name = "editor_test",
    size = "medium",
    srcs = [
        "editor.py",
    ],
    args = [
        "--self_test=True",
    ],
    main = "editor.py",
    srcs_version = "PY2AND3",
    deps = [
        ":data_utils",
        ":seq2seq_model",
        "//tensorflow:tensorflow_py",
    ],
)

filegroup(
    name = "all_files",
    srcs = glob(
        ["**/*"],
        exclude = [
            "**/METADATA",
            "**/OWNERS",
        ],
    ),
    visibility = ["//tensorflow:__subpackages__"],
)
