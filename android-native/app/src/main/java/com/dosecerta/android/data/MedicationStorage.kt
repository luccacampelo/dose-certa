package com.dosecerta.android.data

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID

class MedicationStorage(context: Context) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun load(): List<Medication> {
        val raw = prefs.getString(KEY_MEDICATIONS, "[]") ?: "[]"
        return runCatching {
            val array = JSONArray(raw)
            buildList {
                for (index in 0 until array.length()) {
                    val item = array.getJSONObject(index)
                    val timesArray = item.optJSONArray("times") ?: JSONArray()
                    val times = buildList {
                        for (timeIndex in 0 until timesArray.length()) {
                            add(timesArray.getString(timeIndex))
                        }
                    }
                    add(
                        Medication(
                            id = item.optString("id", UUID.randomUUID().toString()),
                            name = item.optString("name", ""),
                            dosage = item.optString("dosage", ""),
                            times = times,
                            notes = item.optString("notes", ""),
                            active = item.optBoolean("active", true),
                        )
                    )
                }
            }
        }.getOrElse { emptyList() }
    }

    fun save(medications: List<Medication>) {
        val array = JSONArray()
        medications.forEach { medication ->
            val item = JSONObject()
            item.put("id", medication.id)
            item.put("name", medication.name)
            item.put("dosage", medication.dosage)
            item.put("notes", medication.notes)
            item.put("active", medication.active)

            val timesArray = JSONArray()
            medication.times.forEach { time -> timesArray.put(time) }
            item.put("times", timesArray)
            array.put(item)
        }

        prefs.edit().putString(KEY_MEDICATIONS, array.toString()).apply()
    }

    companion object {
        private const val PREFS_NAME = "dose_certa_android"
        private const val KEY_MEDICATIONS = "medications"
    }
}
