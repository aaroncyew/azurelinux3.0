FROM mcr.microsoft.com/cbl-mariner/tmp_pkgbuild_2.0

COPY resources/_enable_repo.sh /enable_repo.sh
COPY resources/_local_repo /etc/yum.repos.d/local_repo.not_a_repo
COPY build_container/welcome.txt /mariner_docker_stuff/welcome.txt
COPY resources/add_shell_functions.txt /mariner_docker_stuff/add_shell_functions.txt
COPY resources/builder_splash.txt /mariner_docker_stuff/splash.txt

RUN echo "alias tdnf='tdnf --releasever=2.0'"                 >> /root/.bashrc && \
    echo "tdnf install -y dnf dnf-plugins-core"                 >> /root/.bashrc && \
    cat /mariner_docker_stuff/add_shell_functions.txt           >> /root/.bashrc && \
    echo "cat /mariner_docker_stuff/splash.txt"                 >> /root/.bashrc && \
    cat /mariner_docker_stuff/welcome.txt                       >> /root/.bashrc && \
    echo "if [[ ! -L /repo ]]; then ln -s /mnt/RPMS/ /repo ; fi" >> /root/.bashrc && \
    echo "cd  /repo"                                            >> /root/.bashrc