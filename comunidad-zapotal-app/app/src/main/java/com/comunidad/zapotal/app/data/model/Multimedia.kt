package com.comunidad.zapotal.app.data.model
import java.io.Serializable

data class Multimedia(
    val id: Int,
    val archivo_url: String,
    val tipo: String,
    val orden: Int
) : Serializable