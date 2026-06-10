package com.comunidad.zapotal.app.data.model

data class ReaccionRequest(

    val tipo: String,
    val usuario: Int,
    val noticia: Int? = null,
    val evento: Int? = null

)