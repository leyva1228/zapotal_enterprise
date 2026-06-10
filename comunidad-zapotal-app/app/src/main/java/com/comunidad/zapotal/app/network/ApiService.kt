package com.comunidad.zapotal.app.network

import com.comunidad.zapotal.app.data.model.*
import okhttp3.MultipartBody
import retrofit2.Call
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    @GET("api/noticias/")
    fun obtenerNoticias(): Call<List<Noticia>>

    @GET("api/eventos/")
    fun obtenerEventos(): Call<List<Evento>>

    @GET("api/autoridades/")
    fun obtenerAutoridades(): Call<List<Autoridad>>

    @POST("api/login/")
    fun login(
        @Body request: LoginRequest
    ): Call<LoginResponse>

    @POST("api/register/")
    fun register(
        @Body request: RegisterRequest
    ): Call<RegisterResponse>

    @POST("api/password_reset/")
    fun forgotPassword(
        @Body request: Map<String, String>
    ): Call<Void>

    @GET("api/usuarios/{id}/")
    fun obtenerUsuarioPorId(
        @Path("id") id: Long
    ): Call<Usuario>

    @PUT("api/usuarios/{id}/")
    fun actualizarUsuario(
        @Path("id") id: Long,
        @Body usuario: Usuario
    ): Call<Usuario>

    @Multipart
    @POST("api/usuarios/{id}/upload_photo/")
    fun subirFotoPerfil(
        @Path("id") id: Long,
        @Part foto: MultipartBody.Part
    ): Call<Usuario>

    // =========================
    // CREAR REACCION
    // =========================

    @POST("api/reacciones/")
    suspend fun crearReaccion(
        @Body reaccion: ReaccionRequest
    ): Response<ReaccionApiResponse>

    // =========================
    // OBTENER CONTEO
    // =========================

    @GET("api/reacciones/conteo/{noticiaId}/")
    suspend fun obtenerConteoReacciones(
        @Path("noticiaId") noticiaId: Int
    ): Response<ReaccionConteoResponse>
}