group "all" {
  targets = ["dbmanager", "topicmanager", "datapump", "apigateway", "web_data_transformer", "data_transformer"]
}

variable "_COMMON_NAME" {
    default= "oda-"
}

variable "TAG" {
    default = "latest"
}

variable "db_manager_port" {
    default = 50000
}

target "dbmanager" {
    context = "src/db_manager"
    dockerfile = "Dockerfile"
    tags = ["${_COMMON_NAME}dbmanager:${TAG}"]
    output = [ "type=docker" ]
}

target "topicmanager" {
    context = "src/topic_manager"
    dockerfile = "Dockerfile"
    tags = ["${_COMMON_NAME}topicmanager:${TAG}"]
    platforms = [
        "linux/amd64",
        # "linux/arm64" actually not needed and impossible to build locally
    ]
    output = [ "type=docker" ]
}

target "datapump" {
    context = "src/data_pump"
    dockerfile = "Dockerfile"
    tags = ["${_COMMON_NAME}datapump:${TAG}"]
    platforms = [
        "linux/amd64",
        # "linux/arm64" actually not needed and impossible to build locally
    ]
    output = [ "type=docker" ]
}

target "apigateway" {
    context = "src/api_gateway"
    dockerfile = "Dockerfile"
    tags = ["${_COMMON_NAME}apigateway:${TAG}"]
    output = [ "type=docker" ]
}

target "web_data_transformer" {
    context = "src/web_data_transformer"
    dockerfile = "Dockerfile"
    tags = ["${_COMMON_NAME}web_data_transformer:${TAG}"]
    output = [ "type=docker" ]
}

target "data_transformer" {
    context = "src/data_transformer"
    dockerfile = "Dockerfile"
    tags = ["${_COMMON_NAME}data_transformer:${TAG}"]
    output = [ "type=docker" ]
}
