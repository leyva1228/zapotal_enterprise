package com.comunidad_zapotal.comunidad_zapotal.ui.eventos

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import com.bumptech.glide.Glide
import com.comunidad_zapotal.comunidad_zapotal.R
import com.comunidad_zapotal.comunidad_zapotal.adapter.MultimediaDetalleAdapter
import com.comunidad_zapotal.comunidad_zapotal.data.model.Multimedia
import com.comunidad_zapotal.comunidad_zapotal.databinding.ActivityEventoDetalleBinding
import com.google.android.material.tabs.TabLayoutMediator
import java.text.SimpleDateFormat
import java.util.Locale

class EventoDetalleActivity : AppCompatActivity() {

    private lateinit var binding: ActivityEventoDetalleBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityEventoDetalleBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // TOOLBAR
        setSupportActionBar(binding.toolbarEvento)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = ""

        binding.toolbarEvento.setNavigationOnClickListener {
            finish()
        }

        // --- RECUPERAR DATOS DEL INTENT (VIENEN DEL BACKEND) ---
        val titulo = intent.getStringExtra("titulo")
        val descripcion = intent.getStringExtra("descripcion")
        val fechaEvento = intent.getStringExtra("fechaEvento")
        val fechaPublicacion = intent.getStringExtra("fechaPublicacion")
        val estado = intent.getStringExtra("estado")
        val autorNombre = intent.getStringExtra("autorNombre")
        val autorFoto = intent.getStringExtra("autorFoto")
        // La categoría por ahora es un ID (Int), lo manejaremos como String según tu diseño
        val categoriaId = intent.getIntExtra("categoria", 0) 
        
        val multimedia = intent.getSerializableExtra("multimedia") as? ArrayList<Multimedia> ?: arrayListOf()

        // --- ASIGNAR DATOS DINÁMICOS ---
        binding.txtTituloEventoDetalle.text = titulo
        binding.txtDescripcionEvento.text = descripcion
        binding.txtAutorEvento.text = autorNombre ?: "Administrador Zapotal"
        binding.txtEstadoEvento.text = estado?.uppercase() ?: "ACTIVO"
        
        // Mapeo temporal de categorías hasta que tengas los nombres en la BD
        binding.txtCategoriaEvento.text = when(categoriaId) {
            1 -> "Cultural"
            2 -> "Deportivo"
            3 -> "Religioso"
            4 -> "Social"
            else -> "General"
        }

        // FOTO PERFIL REAL
        Glide.with(this)
            .load(autorFoto)
            .placeholder(R.drawable.ic_profile)
            .error(R.drawable.ic_profile)
            .circleCrop()
            .into(binding.imgAutorEvento)

        // FECHA PUBLICACION DINÁMICA
        try {
            val fechaLimpia = fechaPublicacion?.replace("Z", "")?.split(".")?.get(0) ?: ""
            val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val outputFormat = SimpleDateFormat("dd 'de' MMMM, yyyy", Locale("es", "ES"))
            inputFormat.parse(fechaLimpia)?.let {
                binding.txtFechaEventoPublicacion.text = outputFormat.format(it)
            }
        } catch (e: Exception) {
            binding.txtFechaEventoPublicacion.text = fechaPublicacion ?: ""
        }

        // FECHA EVENTO DINÁMICA
        try {
            val inputFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            val outputFormat = SimpleDateFormat("dd 'de' MMMM 'de' yyyy", Locale("es", "ES"))
            inputFormat.parse(fechaEvento ?: "")?.let {
                binding.txtFechaEventoInfo.text = outputFormat.format(it)
            }
        } catch (e: Exception) {
            binding.txtFechaEventoInfo.text = fechaEvento ?: ""
        }

        // HORA EVENTO DINÁMICA
        try {
            // Nota: Aquí asumo que la hora viene en la fecha de publicación o tienes un campo hora.
            // Si tienes un campo hora específico en el backend, úsalo aquí.
            val fechaLimpia = fechaPublicacion?.replace("Z", "")?.split(".")?.get(0) ?: ""
            val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val outputFormat = SimpleDateFormat("hh:mm a", Locale("es", "ES"))
            inputFormat.parse(fechaLimpia)?.let {
                binding.txtHoraEvento.text = outputFormat.format(it)
            }
        } catch (e: Exception) {
            binding.txtHoraEvento.text = "--:--"
        }

        // MULTIMEDIA CON LÓGICA DE CARRUSEL
        if (multimedia.isNotEmpty()) {
            binding.cardMultimedia.visibility = View.VISIBLE
            binding.viewPagerEvento.adapter = MultimediaDetalleAdapter(multimedia)
            
            // Solo muestra los puntos si hay más de una imagen
            if (multimedia.size > 1) {
                binding.tabLayoutDots.visibility = View.VISIBLE
                TabLayoutMediator(binding.tabLayoutDots, binding.viewPagerEvento) { _, _ -> }.attach()
            } else {
                binding.tabLayoutDots.visibility = View.GONE
            }
        } else {
            binding.cardMultimedia.visibility = View.GONE
        }

        // COMPARTIR DINÁMICO
        binding.btnCompartirEvento.setOnClickListener {
            val textoCompartir = buildString {
                appendLine("📅 *${titulo}*")
                appendLine()
                appendLine(descripcion)
                appendLine()
                appendLine("📍 Fecha: ${binding.txtFechaEventoInfo.text}")
                appendLine("👤 Publicado por: ${binding.txtAutorEvento.text}")
                appendLine()
                appendLine("Comunidad Zapotal App")
            }
            val shareIntent = Intent().apply {
                action = Intent.ACTION_SEND
                putExtra(Intent.EXTRA_TEXT, textoCompartir)
                type = "text/plain"
            }
            startActivity(Intent.createChooser(shareIntent, "Compartir evento"))
        }

        // MENU DE OPCIONES (PARA REPORTES)
        binding.btnMenuEvento.setOnClickListener {
            // Se implementará más adelante
        }
    }
}
