package com.comunidad_zapotal.comunidad_zapotal.ui.noticias

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import com.bumptech.glide.Glide
import com.comunidad_zapotal.comunidad_zapotal.R
import com.comunidad_zapotal.comunidad_zapotal.adapter.MultimediaDetalleAdapter
import com.comunidad_zapotal.comunidad_zapotal.data.model.Multimedia
import com.comunidad_zapotal.comunidad_zapotal.databinding.ActivityNoticiaDetalleBinding
import com.google.android.material.tabs.TabLayoutMediator
import java.text.SimpleDateFormat
import java.util.Locale

class NoticiaDetalleActivity : AppCompatActivity() {

    private lateinit var binding: ActivityNoticiaDetalleBinding
    private var minutosLeyendo = 0
    private val handler = Handler(Looper.getMainLooper())
    
    // Timer que actualiza SOLO el contador de lectura debajo del título
    private val actualizarTiempoLectura = object : Runnable {
        override fun run() {
            minutosLeyendo++
            binding.txtLeyendoHace.text = "Leyendo hace $minutosLeyendo min"
            handler.postDelayed(this, 60000)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityNoticiaDetalleBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // TOOLBAR
        setSupportActionBar(binding.toolbarNoticia)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = ""
        binding.toolbarNoticia.setNavigationOnClickListener { finish() }

        // --- RECUPERAR DATOS ---
        val titulo = intent.getStringExtra("titulo")
        val contenido = intent.getStringExtra("contenido")
        val fecha = intent.getStringExtra("fecha")
        val autorNombre = intent.getStringExtra("autorNombre")
        val autorFoto = intent.getStringExtra("autorFoto")
        val estado = intent.getStringExtra("estado")
        val multimedia = intent.getSerializableExtra("multimedia") as? ArrayList<Multimedia> ?: arrayListOf()

        // --- ASIGNAR DATOS ---
        binding.txtTituloNoticiaDetalle.text = titulo
        binding.txtContenidoNoticiaDetalle.text = contenido
        binding.txtAutorNoticiaDetalle.text = autorNombre ?: "Redactor Zapotal"
        binding.txtEstadoNoticia.text = estado?.uppercase() ?: "ACTIVO"
        binding.txtLeyendoHace.text = "Iniciando lectura..."

        Glide.with(this)
            .load(autorFoto)
            .placeholder(R.drawable.ic_profile)
            .error(R.drawable.ic_profile)
            .circleCrop()
            .into(binding.imgAutorNoticiaDetalle)

        // FORMATEAR FECHA (Se asigna el valor directo, el label está en el XML)
        try {
            val fechaLimpia = fecha?.replace("Z", "")?.split(".")?.get(0) ?: ""
            val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val outputFormat = SimpleDateFormat("dd MMMM yyyy", Locale("es", "ES"))
            inputFormat.parse(fechaLimpia)?.let {
                binding.txtFechaNoticiaDetalle.text = outputFormat.format(it)
            }
        } catch (e: Exception) {
            binding.txtFechaNoticiaDetalle.text = fecha ?: ""
        }

        // Iniciar timer de lectura cada minuto
        handler.postDelayed(actualizarTiempoLectura, 60000)

        // MULTIMEDIA
        if (multimedia.isNotEmpty()) {
            binding.cardMultimediaNoticia.visibility = View.VISIBLE
            binding.viewPagerNoticia.adapter = MultimediaDetalleAdapter(multimedia)
            if (multimedia.size > 1) {
                binding.tabLayoutDotsNoticia.visibility = View.VISIBLE
                TabLayoutMediator(binding.tabLayoutDotsNoticia, binding.viewPagerNoticia) { _, _ -> }.attach()
            } else {
                binding.tabLayoutDotsNoticia.visibility = View.GONE
            }
        } else {
            binding.cardMultimediaNoticia.visibility = View.GONE
        }

        // BOTON COMPARTIR
        binding.btnShareNoticia.setOnClickListener {
            val textoCompartir = buildString {
                appendLine("📰 *${titulo}*")
                appendLine()
                appendLine(contenido)
                appendLine()
                appendLine("👤 Publicado por: ${binding.txtAutorNoticiaDetalle.text}")
                appendLine("Comunidad Zapotal App")
            }
            val shareIntent = Intent().apply {
                action = Intent.ACTION_SEND
                putExtra(Intent.EXTRA_TEXT, textoCompartir)
                type = "text/plain"
            }
            startActivity(Intent.createChooser(shareIntent, "Compartir noticia"))
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacks(actualizarTiempoLectura)
    }
}
