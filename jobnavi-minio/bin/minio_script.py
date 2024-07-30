from minio import Minio, InvalidResponseError, S3Error
import os
import shutil
import hashlib
from environs import Env
import sys
import logging

root_dir = "/data/"
log_dir = os.path.join(root_dir, "logs")


class MyLogger():
    def __init__(self):
        # 创建一个日志器
        self.logger = logging.getLogger("logger")

        # 设置日志输出的最低等级,低于当前等级则会被忽略
        self.logger.setLevel(logging.INFO)

        # 创建处理器：sh为控制台处理器，fh为文件处理器
        sh = logging.StreamHandler()

        # 创建处理器：sh为控制台处理器，fh为文件处理器,log_file为日志存放的文件夹
        # log_file = os.path.join(log_dir,"{}_log".format(time.strftime("%Y/%m/%d",time.localtime())))
        log_file = os.path.join(log_dir, "minio_info.log")
        fh = logging.FileHandler(log_file, encoding="UTF-8")

        # 创建格式器,并将sh，fh设置对应的格式
        formator = logging.Formatter(fmt="%(asctime)s %(filename)s %(levelname)s %(message)s",
                                     datefmt="%Y/%m/%d %X")
        sh.setFormatter(formator)
        fh.setFormatter(formator)

        # 将处理器，添加至日志器中
        self.logger.addHandler(sh)
        self.logger.addHandler(fh)


logprint = MyLogger().logger


# MinIO使用bucket（桶）来组织对象。
# bucket类似于文件夹或目录，其中每个bucket可以容纳任意数量的对象。
class MINIO:

    def __init__(self, minio_address, minio_admin, minio_password):
        # 通过ip 账号 密码 连接minio server
        # Http连接 将secure设置为False
        self.minioClient = Minio(endpoint=minio_address,
                                 access_key=minio_admin,
                                 secret_key=minio_password,
                                 secure=False)

    def create_one_bucket(self, bucket_name):
        # 创建桶(调用make_bucket api来创建一个桶)
        """
        桶命名规则：小写字母，句点，连字符和数字 允许使用 长度至少3个字符
        使用大写字母、下划线等会报错
        """
        try:
            # bucket_exists：检查桶是否存在
            if self.minioClient.bucket_exists(bucket_name=bucket_name):
                logprint.info("该存储桶已经存在")
            else:
                self.minioClient.make_bucket(bucket_name=bucket_name)
                logprint.info(f"{bucket_name}桶创建成功")
        except InvalidResponseError as err:
            logprint.error(err)

    def upload_file_to_bucket(self, bucket_name, file_name, file_path):
        """
        将文件上传到bucket
        :param bucket_name: minio桶名称
        :param file_name: 存放到minio桶中的文件名字(相当于对文件进行了重命名，可以与原文件名不同)
                            file_name处可以创建新的目录(文件夹) 例如 /example/file_name
                            相当于在该桶中新建了一个example文件夹 并把文件放在其中
        :param file_path: 本地文件的路径
        """
        # 桶是否存在 不存在则新建
        check_bucket = self.minioClient.bucket_exists(bucket_name)
        if not check_bucket:
            self.minioClient.make_bucket(bucket_name)

        try:
            self.minioClient.fput_object(bucket_name=bucket_name,
                                         object_name=file_name,
                                         file_path=file_path)
        except FileNotFoundError as err:
            logprint.error('upload_failed: ' + str(err))
        except S3Error as err:
            logprint.error("upload_failed:", err)

    def download_file_from_bucket(self, bucket_name, minio_file_path, download_file_path):
        """
        从bucket下载文件
        :param bucket_name: minio桶名称
        :param minio_file_path: 存放在minio桶中文件名字
                            file_name处可以包含目录(文件夹) 例如 /example/file_name
        :param download_file_path: 文件获取后存放的路径
        """
        # 桶是否存在
        check_bucket = self.minioClient.bucket_exists(bucket_name)
        if check_bucket:
            try:
                self.minioClient.fget_object(bucket_name=bucket_name,
                                             object_name=minio_file_path,
                                             file_path=download_file_path)
                minio_md5 = self.minio_objects_md5(bucket_name, minio_file_path)
                local_md5 = self.local_objects_md5(download_file_path)
                print("校验文件md5: minio-->" + minio_md5 + "/local-->" + local_md5)
                if minio_md5 != local_md5:
                    raise ValueError("md5不一致,请核验!!!")
            except FileNotFoundError as err:
                logprint.error('download_failed: ' + str(err))
            except S3Error as err:
                logprint.error("download_failed:", err)

    def download_all_pbjects_from_bucket(self, bucket_name, minio_file_path, download_file_path):
        """
        从bucket下载所有文件
        :param bucket_name: minio桶名称
        :param minio_file_path: 存放在minio桶中文件名字
                            file_name处可以包含目录(文件夹) 例如 /example/file_name
        :param download_file_path: 文件获取后存放的路径
        """
        list_objects = self.get_list_objects_from_bucket_dir(bucket_name, minio_file_path)
        logprint.info(
            "start pull objects from minio----->" + "bucket_name: " + bucket_name + " minio_file_path: " + minio_file_path)
        try:
            for obeject_path in list_objects:
                logprint.info("开始拉取文件: " + obeject_path + "--->" + download_file_path + obeject_path)
                self.download_file_from_bucket(bucket_name, obeject_path, download_file_path + obeject_path)
            count = list_objects.__len__()
            logprint.info("结束拉取----->successful!--->共计: " + str(count))
        except Exception as err:
            logprint.info("从minio上拉取文件部分失败!!!", err)
            shutil.rmtree(download_file_path)

    # 获取所有的桶
    def get_all_bucket(self):
        buckets = self.minioClient.list_buckets()
        ret = []
        for _ in buckets:
            ret.append(_.name)
        return ret

    # 获取桶里某个目录下的所有目录和文件
    def get_list_objects_from_bucket_dir(self, bucket_name, dir_name):
        # 桶是否存在
        check_bucket = self.minioClient.bucket_exists(bucket_name)
        if check_bucket:
            # 获取到bucket_name桶中的dir_name下的所有目录和文件
            # prefix 获取的文件路径需包含该前缀
            objects = self.minioClient.list_objects(bucket_name=bucket_name,
                                                    prefix=dir_name,
                                                    recursive=True)
            ret = []
            for _ in objects:
                ret.append(_.object_name)
            return ret

    def minio_objects_md5(self, bucket_name, object_name):
        # 桶是否存在

        check_bucket = self.minioClient.bucket_exists(bucket_name)
        if check_bucket:
            md5 = self.minioClient.get_object(bucket_name=bucket_name,
                                              object_name=object_name)
            return md5.headers['etag'].replace('"', '')

    def local_objects_md5(self, local_path):
        md5 = hashlib.md5()
        with open(local_path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                md5.update(chunk)
        return md5.hexdigest()


def env_main():
    env = Env()
    # minio登录IP地址和账号密码
    minio_address = env.str("minio_address", "10.253.199.238:9000")
    minio_admin = env.str("minio_admin", "minioadmin")
    minio_password = env.str("minio_password", "Pass@op1s@op1s")
    minio_bucket = env.str("minio_bucket", 'jobnavi310')
    minio_adaptor_storage_path = 'data/bkee/bkdata/jobnavirunner/adaptor/' + env.str("adaptor_task", "batch_sql")
    minio_env_storage_path = 'data/bkee/bkdata/jobnavirunner/env/' + env.str("env_task", "")
    minio_download_path = env.str("minio_download_path", '/Users/chenzeng/batch_sql/')
    minio_gen = MINIO(minio_address=minio_address,
                      minio_admin=minio_admin,
                      minio_password=minio_password)

    if len(env.str("adaptor_task", "")) != 0:
        minio_gen.download_all_pbjects_from_bucket(minio_bucket, minio_adaptor_storage_path, minio_download_path)
    if len(env.str("env_task", "")) != 0:
        minio_gen.download_all_pbjects_from_bucket(minio_bucket, minio_env_storage_path, minio_download_path)


def shell_main():
    logprint.info(sys.argv)
    minio_address = sys.argv[1]
    minio_admin = sys.argv[2]
    minio_password = sys.argv[3]
    minio_bucket = sys.argv[4]
    minio_adaptor_storage_path = 'data/bkee/bkdata/jobnavirunner/adaptor/' + sys.argv[5]
    minio_env_storage_path = 'data/bkee/bkdata/jobnavirunner/env/' + sys.argv[6]
    minio_download_path = sys.argv[7]
    minio_gen = MINIO(minio_address=minio_address,
                      minio_admin=minio_admin,
                      minio_password=minio_password)
    if len(sys.argv[5]) != 0:
        minio_gen.download_all_pbjects_from_bucket(minio_bucket, minio_adaptor_storage_path, minio_download_path)
    if len(sys.argv[6]) != 0:
        minio_gen.download_all_pbjects_from_bucket(minio_bucket, minio_env_storage_path, minio_download_path)


if __name__ == "__main__":
    #     env_main()
    shell_main()
