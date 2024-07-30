package com.tencent.bk.base.dataflow.jobnavi.controller;

import com.tencent.bk.base.dataflow.jobnavi.common.MinioRequest;
import com.tencent.bk.base.dataflow.jobnavi.common.Result;
import io.swagger.annotations.Api;

import io.swagger.annotations.ApiOperation;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;


import java.io.IOException;
import java.util.Map;

/**
 * @Author chenzeng
 * @Date 2023/3/10 17:11
 * @DESC
 */
@Slf4j
@RestController
@RequestMapping("minio")
@Api(tags = "minio操作")
public class MinioController {

    @PostMapping("/pull")
    @ApiOperation("拉取minio信息")
    public Result pullMinio(@RequestBody MinioRequest minioRequest) {

        String startCommand = "/data/bin/task_start_python.sh" + " " + minioRequest.getMinio_address() + " " + minioRequest.getMinio_admin() + "  "
                + minioRequest.getMinio_password() + " " + minioRequest.getMinio_bucket() + " " + minioRequest.getAdaptor_task() + " "
                + minioRequest.getEnv_task() + " " + minioRequest.getMinio_download_path();
        try {
            // start task minio pulling
            log.info("minio task, command is " + startCommand);
            ProcessBuilder builder = new ProcessBuilder("/bin/bash", "-c", startCommand);
            Map<String, String> processEnv = builder.environment();
            processEnv.put("minio_address", minioRequest.getMinio_address());
            log.info("mino_address ---> " + processEnv.get("minio_address"));
            Process process = builder.start();
            int status = process.waitFor();
            if (status != 0) {
                throw new Exception("Process result is not zero.");
            }
        } catch (Exception e) {
            log.warn("Running task error." , e);
            return Result.failed(e.getMessage());
        }
        return Result.succeed("success");
    }


}
