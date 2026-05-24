package com.comunidad_zapotal.comunidad_zapotal.data.model
import com.comunidad_zapotal.comunidad_zapotal.data.model.Multimedia

data class Evento(
    val id: Int = 0,
    val titulo: String? = null,
    val descripcion: String? = null,
    val fecha_evento: String? = null,
    val fecha_publicacion: String? = null,
    val estado: String? = null,
    val categoria: Int = 0,
    val usuario: Usuario,
    val multimedia: List<Multimedia> = emptyList()
)