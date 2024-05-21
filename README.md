## 개요

Name resolution을 요청하는 client와 DNS server의 역할을 하는 프로세스들이 UDP 통신을 통해 가상의 DNS 서비스를 시뮬레이션한다.

<div style="display: flex; justify-content: space-between;">
    <img src="https://github.com/jiseokson/dns_simulation/assets/70203010/696a9742-9703-4bec-aebc-7a9d9f9537cb" alt="Iterarive query" width="45%">
    <img src="https://github.com/jiseokson/dns_simulation/assets/70203010/f8946326-dd63-4346-9b44-7cdee305a091" alt="Recursive query" width="45%">
</div>

## 실행

해당 프로젝트는 `macOS Sonoma 14.3.1`, `python 3.12.3`에서 작성되고 테스트되었다.
정상적인 실행을 위해서는

  - 실행 스크립트(`client`, `localDNSServer`, `rootDNSServer`, `comTLDDNSServer`, `companyDNSServer`) 파일에 실행 권한이 부여되었는지
  - shebang이 운영체제에 의해서 지원 가능한지
  - `python` 버전이 해당 프로젝트의 실행을 지원하는지
  - 설정 파일(`config.txt`와 각 회사의 RR cache 파일)과 프로그램 실행 인자가 올바른지

등을 확인해야 한다.

## 테스트

다음의 설정에서 `client`, `localDNSServer`, `rootDNSServer`, `comTLDDNSServer`와 `abc`, `gogle`이라는 회사 이름으로 `companyDNSServer`를 실행했다.

  - `config.txt`
    ```
    local_dns_server = [dns.dreamnet.com, 100.100.100.100] 20001
    root_dns_server = [dns.rootDSNService.com, 57.32.9.101] 20002
    comTLD_dns_server = [dns.comTLDDNSService.com, 30.10.2.102] 20003
    abc_dns_server = [dns.abc.com, 77.108.19.103] 30000
    gogle_dns_server = [dns.gogle.com, 17.134.2.204] 30001
    ```
  - `abc.txt`
    ```
    machine1.abc.com, 77.88.99.49, A
    ftp.abc.com, machine1.abc.com, CNAME
    www.abc.com, machine1.abc.com, CNAME
    ```
  - `gogle.txt`
    ```
    machine1.gogle.com, 17.134.2.45, A
    machine2.gogle.com, 17.134.2.46, A
    ftp.gogle.com, machine1.gogle.com, CNAME
    www.gogle.com, machine1.gogle.com, CNAME
    media.gogle.com, machine2.gogle.com, CNAME
    ```
