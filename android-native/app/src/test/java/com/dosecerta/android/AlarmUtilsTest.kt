package com.dosecerta.android

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class AlarmUtilsTest {
    @Test
    fun parseTimesCsv_sortsAndDeduplicates() {
        val parsed = AlarmUtils.parseTimesCsv("20:00, 08:00, 08:00")
        assertEquals(listOf("08:00", "20:00"), parsed)
    }

    @Test
    fun parseTimesCsv_rejectsInvalid() {
        val ex = runCatching { AlarmUtils.parseTimesCsv("08:00, 25:99") }.exceptionOrNull()
        assertTrue(ex is IllegalArgumentException)
    }

    @Test
    fun buildAlarmMessage_containsTitleAndNotes() {
        val message = AlarmUtils.buildAlarmMessage(
            medicationName = "Losartana",
            dosage = "50mg",
            doseTime = "08:00",
            notes = "Tomar apos cafe.",
        )
        assertTrue(message.contains("Titulo: Losartana (50mg)"))
        assertTrue(message.contains("Observacoes: Tomar apos cafe."))
    }
}
