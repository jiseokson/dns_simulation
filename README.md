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
    root_dns_server = [dns.rootDNSService.com, 57.32.9.101] 20002
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

실행 명령은 다음과 같다.
```
$ ./client 20000
$ ./localDNSServer 20001
$ ./rootDNSServer 20002
$ ./comTLDDNSServer 20003
$ ./companyDNSServer 30000 abc.txt
$ ./companyDNSServer 30001 gogle.txt
```

  - ### Root DNS Server, com TLD DNS Server 모두 recursive query 수락하지 않는 경우
    Local DNS Server로부터 iterative query가 실행되는 모습을 확인할 수 있으며 qeury중 새로 알려진 RR이 Local DNS Server의 cache에 저장됨을 확인할 수 있다.
    ![image](https://github.com/jiseokson/dns_simulation/assets/70203010/1b31b352-9a58-4a04-b26d-076941b2c6cb)
  - ### Root DNS Server만 recursive query를 수락하는 경우
    Root DNS Server가 Local DNS Server의 recursive query를 처리하기로 수락했으므로, Root DNS Server의 query를 수신받은 com TLD DNS Server는 자신의 recursive query 처리 여부와 상관없이 recursive query를 수행해야 한다. Recursive qeury가 수행되는 모습과 Local DNS Server에 최종적으로 알려진 `ftp.gogle.com`의 RR만 caching된 것을 확인할 수 있다. Root DNS Server와 com TLD DNS Server 모두 recursive query를 처리하도록 설정되어 있어도 같은 동작을 한다.
    ![image](https://github.com/jiseokson/dns_simulation/assets/70203010/17c21491-e96e-4493-88b9-9408739791c1)
  - ### com TLD DNS Server만 recursive query를 수락하는 경우
    com TLD DNS server 이후로 recursive query가 수행되는 모습을 확인할 수 있다.
    ![image](https://github.com/jiseokson/dns_simulation/assets/70203010/0da57259-c500-425e-abb5-b2cc53e4b17c)



