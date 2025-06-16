# Instalação do TaleonTracker em LXC Debian

Este guia descreve como instalar e configurar o TaleonTracker em um container LXC Debian.

## Pré-requisitos

- Container LXC com Debian 11 ou superior
- Acesso root ao container
- Conexão com a internet

## Passos de Instalação

1. Copie o script de instalação para o container:
```bash
scp setup_lxc.sh root@<ip-do-container>:/root/
```

2. Acesse o container via SSH:
```bash
ssh root@<ip-do-container>
```

3. Torne o script executável e execute-o:
```bash
chmod +x setup_lxc.sh
./setup_lxc.sh
```

## Verificação da Instalação

Após a instalação, você pode verificar se o serviço está rodando com os seguintes comandos:

```bash
# Verificar status do serviço
systemctl status taleontracker

# Verificar logs do serviço
journalctl -u taleontracker

# Verificar se o Nginx está rodando
systemctl status nginx
```

## Acessando a API

A API estará disponível em:
- http://<ip-do-container>/api/

## Logs

Os logs do serviço podem ser encontrados em:
- `/var/log/taleontracker.err.log`
- `/var/log/taleontracker.out.log`

## Reiniciando o Serviço

Para reiniciar o serviço:
```bash
systemctl restart taleontracker
```

## Desinstalação

Para desinstalar o serviço:
```bash
systemctl stop taleontracker
systemctl disable taleontracker
rm /etc/systemd/system/taleontracker.service
rm -rf /opt/taleontracker
``` 