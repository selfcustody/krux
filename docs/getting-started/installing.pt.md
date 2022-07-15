Esta página explica como instalar o Krux de uma versão oficial pré-construída. Se você quiser construir e instalar o Krux a partir da fonte, por gentileza leia o guia [Instalando a partir do código-fonte](../installing-from-source).

### Requisitos
#### Hardware

Você irá precisar do M5StickV, de um cabo USB-C e um computador com uma porta USB para continuar. Consulte a [lista de peças](../../parts) para mais informações.

Se você deseja realizar atualizações de firmware sem conectar a um computador (_airgapped_), deseja configurações persistentes, ou deseja usar o Krux em um idioma diferente, você também precisará de um [cartao microSD suportado](https://github.com/m5stack/m5-docs/blob/master/docs/en/core/m5stickv.md#tf-cardmicrosd-test).

### Baixe a última versão
Acesse a página de lançamentos [lançamentos](https://github.com/selfcustody/krux/releases) e baixe a última versão assinada.

### Verifique os arquivos
Antes de instalar a versão, é uma boa ideia checar se:

1. O _hash_ SHA256 do arquivo `krux-vX.Y.Z.zip` corresponde ao hash de `krux-vX.Y.Z.zip.sha256.txt`
2. O arquivo de assinatura `krux-vX.Y.Z.zip.sig` pode ser verificado com a [chave pública `selfcustody.pem`](https://github.com/selfcustody/krux/blob/main/selfcustody.pem) encontrado na raiz do repositório krux.

Você pode fazer isso manualmente, ou com o shell script `krux` que contém comandos auxiliares para isso:

```bash
./krux sha256 krux-vX.Y.Z.zip
./krux verify krux-vX.Y.Z.zip selfcustody.pem
```

Curiosidade: Cada lançamento do Krux é assinado com a Krux!

### Atualize o firmware no M5StickV
Conecte o M5StickV ao seu computador por meio do USB, ligue-o (botão do lado esquerdo) e execute o seguinte:

```bash
unzip krux-vX.Y.Z.zip && cd krux-vX.Y.Z
./ktool -B goE -b 1500000 maixpy_m5stickv/kboot.kfpkg
```

Se o `ktool` falhar na execução, você pode precisar dar a ele permissão de executável com `chmod +x ./ktool`, ou no Windows ou Mac permitir explicitamente que o arquivo seja executável, adicionando uma exceção para ele.

Se o processo de _flash_ falhar no meio do caminho, verifique a conexão, reinicie o dispositivo e tente o comando novamente.

Quando o processo de flash estiver concluído, você deverá ver...

<img src="../../img/logo-150.png">

Se após 30 segundos você ainda ver uma tela preta, tente desligar o dispositivo mantendo pressionado o botão liga/desliga por seis segundos.

Parabéns, agora você está executando o Krux!

### Suporte Multilíngue
<img src="../../img/login-locale-de-de-150.png" align="right">

Prefere um idioma diferente? Krux tem suporte para muitos idiomas, incluindo:


- de-DE (Alemão)
- es-MX (Espanhol)
- fr-FR (Francês)
- vi-VN (Vietnamita)
- pt-BR (Português do Brasil)
- Estamos sentindo falta de um? Faça um PR!

Para usar uma tradução, primeiro copie a pasta [`i18n/translations`](https://github.com/selfcustody/krux/tree/main/i18n/translations) para uma pasta `translations` na raiz de um cartão microSD formatado como FAT-32, insira o cartão no seu M5StickV e reinicie o dispositivo. Uma vez na tela inicial, selecione `Settings`, seguido por `Locale` e s selecione o idioma que você deseja usar. Sua preferência será salva automaticamente no arquivo `settings.json`, na raiz do seu cartão microSD.

### Atualize via cartão microSD
Depois de instalar o _firmware_ inicial em seu dispositivo por meio do USB, você pode tanto continuar atualizando o dispositivo por _flashing_ ou pode realizar atualizações via cartão microSD para manter o dispositivo sem qualquer conexão USB.

Para realizar uma atualização, simplesmente copie os arquivos `firmware.bin` e `firmware.bin.sig` para a raiz de um cartão microSD formatado como FAT-32, insira o cartão em seu M5StickV e reinicie o dispositivo. Se ele detectar o novo arquivo de _firmware_ e puder verificar a assinatura, você será solicitado a instalá-lo.

Quando a instalação estiver concluída, ejete o cartão microSD e exclua os arquivos de _firmware_ antes de reinserir e reinicializar.
