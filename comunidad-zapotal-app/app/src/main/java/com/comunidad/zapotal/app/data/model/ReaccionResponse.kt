package com.comunidad.zapotal.app.data.model

data class ReaccionResponse(
    val id: Int,
    val tipo: String?,
    val usuario: Int,
    val noticia: Int?,
    val evento: Int?,
    val accion: String?
)