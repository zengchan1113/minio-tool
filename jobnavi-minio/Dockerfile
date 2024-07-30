FROM registry.paas/ops/python:3.7

# java 8安装
RUN mkdir -p /usr/lib/jdk8
COPY ./lib/openjdk-8u43-linux-x64.tar.gz ./
RUN tar -xvzf openjdk-8u43-linux-x64.tar.gz -C /usr/lib/jdk8 --strip-components 1
RUN rm openjdk-8u43-linux-x64.tar.gz
ENV JAVA_HOME /usr/lib/jdk8
ENV CLASSPATH $JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
ENV PATH $JAVA_HOME/bin:$PATH


WORKDIR /data
RUN mkdir bin logs
COPY ./target/jobnavi-minio-*.jar app.jar
COPY ./bin/* ./bin/
RUN chmod 755 ./bin/* && \
    chmod 755 /data/app.jar
ENTRYPOINT ["sh","/data/bin/start.sh"]