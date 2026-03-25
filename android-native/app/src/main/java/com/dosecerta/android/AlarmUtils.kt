package com.dosecerta.android

object AlarmUtils {
    private val timePattern = Regex("^(?:[01]\\d|2[0-3]):[0-5]\\d$")

    fun parseHourMinute(value: String): Pair<Int, Int>? {
        if (!timePattern.matches(value)) {
            return null
        }

        val parts = value.split(":")
        return parts[0].toInt() to parts[1].toInt()
    }

    fun parseTimesCsv(raw: String): List<String> {
        val normalized = raw.replace(";", ",")
        val values = normalized.split(",").map { it.trim() }.filter { it.isNotEmpty() }

        if (values.isEmpty()) {
            throw IllegalArgumentException("Informe ao menos um horario no formato HH:MM.")
        }

        val invalid = values.filterNot { timePattern.matches(it) }
        if (invalid.isNotEmpty()) {
            throw IllegalArgumentException("Horarios invalidos: ${invalid.joinToString(", ")}")
        }

        return values
            .distinct()
            .sortedWith(compareBy({ parseHourMinute(it)?.first }, { parseHourMinute(it)?.second }))
    }

    fun buildAlarmMessage(
        medicationName: String,
        dosage: String,
        doseTime: String,
        notes: String,
    ): String {
        val base = "Titulo: $medicationName ($dosage) | Horario: $doseTime"
        val cleanNotes = notes.trim()
        return if (cleanNotes.isEmpty()) {
            "$base | Observacoes: sem observacoes"
        } else {
            "$base | Observacoes: $cleanNotes"
        }
    }
}
