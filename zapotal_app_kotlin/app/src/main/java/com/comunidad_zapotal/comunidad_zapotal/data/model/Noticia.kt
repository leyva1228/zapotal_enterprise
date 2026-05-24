package com.comunidad_zapotal.comunidad_zapotal.data.model

import com.comunidad_zapotal.comunidad_zapotal.data.model.Multimedia
import android.os.Parcelable
data class Noticia(
    val id: Int,
    val titulo: String,
    val contenido: String,
    val fecha_publicacion: String,
    val estado: String,
    val usuario: Usuario,
    val multimedia: List<Multimedia>
)