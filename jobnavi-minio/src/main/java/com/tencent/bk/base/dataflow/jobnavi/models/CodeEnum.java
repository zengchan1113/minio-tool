package com.tencent.bk.base.dataflow.jobnavi.models;

/**
 * @Author chenzeng
 * @Date 2022/12/29 19:06
 * @DESC
 */
public enum CodeEnum {
    SUCCESS("1500200","成功"),
    ERROR("1","失败"),
    WARNING("2","警告"),
    ;


    private String code;
    private String msg;

    CodeEnum(String code){
        this.code = code;
    }

    private CodeEnum(String code, String msg)
    {
        this.code = code;
        this.msg = msg;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }
}
