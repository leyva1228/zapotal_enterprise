package com.comunidad.zapotal.app.data.model

import com.comunidad.zapotal.app.data.model.Multimedia
import android.os.Parcelable

data class Noticia(
    val id: Int,
    val titulo: String,
    val contenido: String,
    val fecha_publicacion: String,
    val estado: String,
    val usuario: Usuario,
    val multimedia: List<Multimedia>,
    val reacciones_count: Int = 0
)