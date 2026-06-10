package com.comunidad.zapotal.app.data.model

data class Usuario(
    val id: Long,
    val nombres: String,
    val apellidos: String,
    val email: String,
    val dni: String,
    val telefono: String?,
    val tipo_usuario: String,
    val estado: String,
    val dni_verificado: Boolean,
    val foto_perfil_url: String?,
    val fecha_registro: String? // Añadido campo fecha de registro
)