package com.comunidad_zapotal.comunidad_zapotal.network

import com.comunidad_zapotal.comunidad_zapotal.data.model.Autoridad
import com.comunidad_zapotal.comunidad_zapotal.data.model.Evento
import com.comunidad_zapotal.comunidad_zapotal.data.model.Noticia
import retrofit2.Call
import retrofit2.http.GET


interface ApiService {

    @GET("api/noticias")
    fun obtenerNoticias(): Call<List<Noticia>>

    @GET("api/eventos")
    fun obtenerEventos(): Call<List<Evento>>

    @GET("api/autoridades")
    fun obtenerAutoridades(): Call<List<Autoridad>>
}