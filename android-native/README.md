# DoseCerta Android Nativo (Kotlin)

Aplicativo Android nativo para cadastrar remedios e criar alarmes direto no app Relogio do celular,
sem depender de navegador.

## Funcionalidades
- Cadastro de medicamento (nome, dosagem, horarios e observacoes)
- Persistencia local no aparelho (SharedPreferences)
- Listagem de medicamentos ativos
- Desativacao de medicamento
- Criacao de alarme direto no Relogio usando `AlarmClock.ACTION_SET_ALARM`

## Requisitos
- Android Studio atualizado
- JDK 17
- Android SDK (API 35)

## Como executar
1. Abra a pasta `android-native` no Android Studio.
2. Aguarde o sync do Gradle.
3. Conecte um celular Android (com depuracao USB) ou inicie um emulador.
4. Clique em `Run`.

## Fluxo de uso
1. Cadastre um medicamento com horarios (exemplo: `08:00, 20:00`).
2. Na lista de medicamentos, toque em `Criar alarme das HH:MM`.
3. O Android abrirá o app Relogio com os campos preenchidos.
4. Confirme e salve o alarme.

## Testes unitarios
No terminal do Android Studio (dentro de `android-native`):

```bash
./gradlew test
```

No Windows PowerShell:

```powershell
.\gradlew.bat test
```

## Observacao sobre wrapper
Se a IDE indicar ausencias no wrapper, use a opcao de sincronizacao/repair do proprio Android Studio,
ou gere novamente via Gradle local (`gradle wrapper`) se necessario.
