package com.comunidad.zapotal.app.data.model

data class Comentario(
    val id: Int,
    val contenido: String,
    val fecha: String,
    val usuario: Usuario,
    val noticiaId: Int? = null,
    val eventoId: Int? = null
)
