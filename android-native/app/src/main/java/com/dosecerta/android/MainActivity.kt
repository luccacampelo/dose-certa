package com.dosecerta.android

import android.content.Context
import android.content.Intent
import android.provider.AlarmClock
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.weight
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.dosecerta.android.data.Medication
import com.dosecerta.android.data.MedicationStorage
import com.dosecerta.android.ui.theme.DoseCertaTheme
import java.util.UUID

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: android.os.Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            DoseCertaTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    DoseCertaScreen()
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun DoseCertaScreen() {
    val context = LocalContext.current
    val storage = remember { MedicationStorage(context) }
    val medications = remember { mutableStateListOf<Medication>() }
    val snackbarHostState = remember { SnackbarHostState() }

    var name by remember { mutableStateOf("") }
    var dosage by remember { mutableStateOf("") }
    var timesRaw by remember { mutableStateOf("") }
    var notes by remember { mutableStateOf("") }

    LaunchedEffect(Unit) {
        medications.clear()
        medications.addAll(storage.load())
    }

    fun persist(items: List<Medication>) {
        medications.clear()
        medications.addAll(items)
        storage.save(items)
    }

    val activeMedications = medications.filter { it.active }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("DoseCerta Android") }
            )
        },
        snackbarHost = { SnackbarHost(hostState = snackbarHostState) },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("Cadastro rapido", style = MaterialTheme.typography.titleMedium)
                    Text(
                        "Adicione remedios e gere alarmes direto no app Relogio.",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }

            OutlinedTextField(
                value = name,
                onValueChange = { name = it },
                label = { Text("Nome do medicamento") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )

            OutlinedTextField(
                value = dosage,
                onValueChange = { dosage = it },
                label = { Text("Dosagem") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )

            OutlinedTextField(
                value = timesRaw,
                onValueChange = { timesRaw = it },
                label = { Text("Horarios (HH:MM, separados por virgula)") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )

            OutlinedTextField(
                value = notes,
                onValueChange = { notes = it },
                label = { Text("Observacoes") },
                modifier = Modifier.fillMaxWidth(),
                minLines = 2,
                maxLines = 3,
            )

            Button(
                onClick = {
                    val cleanName = name.trim()
                    val cleanDosage = dosage.trim()

                    if (cleanName.isEmpty()) {
                        showToast(context, "Informe o nome do medicamento.")
                        return@Button
                    }
                    if (cleanDosage.isEmpty()) {
                        showToast(context, "Informe a dosagem.")
                        return@Button
                    }

                    val parsedTimes = runCatching { AlarmUtils.parseTimesCsv(timesRaw) }
                        .getOrElse {
                            showToast(context, it.message ?: "Horario invalido.")
                            return@Button
                        }

                    val medication = Medication(
                        id = UUID.randomUUID().toString(),
                        name = cleanName,
                        dosage = cleanDosage,
                        times = parsedTimes,
                        notes = notes.trim(),
                        active = true,
                    )

                    val updated = medications.toList() + medication
                    persist(updated)

                    name = ""
                    dosage = ""
                    timesRaw = ""
                    notes = ""
                    showToast(context, "Medicamento cadastrado.")
                },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text("Salvar medicamento")
            }

            Spacer(modifier = Modifier.height(2.dp))
            Text("Medicamentos ativos", style = MaterialTheme.typography.titleLarge)

            if (activeMedications.isEmpty()) {
                Text(
                    "Nenhum medicamento ativo cadastrado.",
                    style = MaterialTheme.typography.bodyMedium,
                )
            }

            activeMedications.forEach { medication ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier.padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    "${medication.name} (${medication.dosage})",
                                    style = MaterialTheme.typography.titleMedium,
                                )
                                val notesText = medication.notes.ifBlank { "sem observacoes" }
                                Text(
                                    "Observacoes: $notesText",
                                    style = MaterialTheme.typography.bodySmall,
                                )
                            }
                            TextButton(onClick = {
                                val updated = medications.map {
                                    if (it.id == medication.id) it.copy(active = false) else it
                                }
                                persist(updated)
                                showToast(context, "Medicamento desativado.")
                            }) {
                                Text("Desativar")
                            }
                        }

                        medication.times.forEach { doseTime ->
                            Button(
                                onClick = {
                                    createClockAlarm(context, medication, doseTime)
                                },
                                modifier = Modifier.fillMaxWidth(),
                            ) {
                                Text("Criar alarme das $doseTime")
                            }
                        }
                    }
                }
            }
        }
    }
}

private fun createClockAlarm(context: Context, medication: Medication, doseTime: String) {
    val parsed = AlarmUtils.parseHourMinute(doseTime)
    if (parsed == null) {
        showToast(context, "Horario invalido: $doseTime")
        return
    }

    val (hour, minute) = parsed
    val message = AlarmUtils.buildAlarmMessage(
        medicationName = medication.name,
        dosage = medication.dosage,
        doseTime = doseTime,
        notes = medication.notes,
    )

    val intent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
        putExtra(AlarmClock.EXTRA_HOUR, hour)
        putExtra(AlarmClock.EXTRA_MINUTES, minute)
        putExtra(AlarmClock.EXTRA_MESSAGE, message)
        putExtra(AlarmClock.EXTRA_VIBRATE, true)
        putExtra(AlarmClock.EXTRA_SKIP_UI, false)
        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    }

    if (intent.resolveActivity(context.packageManager) != null) {
        context.startActivity(intent)
    } else {
        showToast(context, "Nenhum app Relogio compativel encontrado no celular.")
    }
}

private fun showToast(context: Context, message: String) {
    Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
}
