package com.tencent.bk.base.dataflow.jobnavi.common;

import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

@Data
public class MinioRequest {

    @ApiModelProperty(value = "minio_address",required = true)
    private String minio_address;

    @ApiModelProperty(value = "minio_admin",required = true)
    private String minio_admin;

    @ApiModelProperty(value = "minio_password",required = true)
    private String minio_password;

    @ApiModelProperty(value = "minio_bucket",required = true)
    private String minio_bucket;

    @ApiModelProperty(value = "adaptor_task",required = true)
    private String adaptor_task;

    @ApiModelProperty(value = "env_task",required = true)
    private String env_task;

    @ApiModelProperty(value = "minio_download_path",required = true)
    private String minio_download_path;

}
