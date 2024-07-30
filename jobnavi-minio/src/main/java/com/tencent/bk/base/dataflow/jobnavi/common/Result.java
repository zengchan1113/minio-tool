package com.tencent.bk.base.dataflow.jobnavi.common;

/**
 * @Author chenzeng
 * @Date 2022/12/29 19:05
 * @DESC
 */

import com.tencent.bk.base.dataflow.jobnavi.models.CodeEnum;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Result<T> implements Serializable {

    private T data;
    private String code;
    private String message;
    private Boolean result;
    private String errors;

    @Override
    public String toString() {
        return String.format("{\"data\": %s,\"code\": %s,\"message\": \"%s\",\"result\": %s}"
                ,data == null? "\"[]\"":data.toString(),code.toString(),message,result.toString());
    }

    public static <T> Result<T> succeed(T model, String msg) {
        return of(model, CodeEnum.SUCCESS.getCode(), msg,true,null);
    }

    public static <T> Result<T> succeed(T model) {
        return of(model, CodeEnum.SUCCESS,true,null);
    }

    public static <T> Result<T> of(T datas, String code, String msg,Boolean result,String errors) {
        return new Result<>(datas, code, msg,result,errors);
    }

    public static <T> Result<T> of(T datas, CodeEnum msg,Boolean result,String errors) {
        return new Result<>(datas, msg.getCode(), msg.getMsg(),result,errors);
    }

    public static <T> Result<T> failed(String msg) {
        return of(null, CodeEnum.ERROR.getCode(), msg,false,null);
    }

    public static <T> Result<T> failed(T model, String msg) {
        return of(model, CodeEnum.ERROR.getCode(), msg,false,null);
    }

    public static <T> Result<T> warning(String msg){
        return of(null, CodeEnum.WARNING.getCode(), msg, false,null);
    }

    public static <T> Result<T> warning(T model,String msg){
        return of(model,CodeEnum.WARNING.getCode(),msg,false,null);
    }
}
