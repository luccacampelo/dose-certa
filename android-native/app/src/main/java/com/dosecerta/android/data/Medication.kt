package com.dosecerta.android.data

data class Medication(
    val id: String,
    val name: String,
    val dosage: String,
    val times: List<String>,
    val notes: String,
    val active: Boolean = true,
)
