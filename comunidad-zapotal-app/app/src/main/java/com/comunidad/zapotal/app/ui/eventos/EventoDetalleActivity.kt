package com.comunidad.zapotal.app.ui.eventos

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.bumptech.glide.Glide
import com.comunidad.zapotal.app.R
import com.comunidad.zapotal.app.adapter.MultimediaDetalleAdapter
import com.comunidad.zapotal.app.data.model.Multimedia
import com.comunidad.zapotal.app.data.model.ReaccionRequest
import com.comunidad.zapotal.app.databinding.ActivityEventoDetalleBinding
import com.comunidad.zapotal.app.network.RetrofitClient
import com.comunidad.zapotal.app.ui.auth.AuthRequiredBottomSheetFragment
import com.comunidad.zapotal.app.ui.noticias.ComentariosBottomSheetFragment
import com.comunidad.zapotal.app.utils.SessionManager
import com.google.android.material.tabs.TabLayoutMediator
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Locale

class EventoDetalleActivity : AppCompatActivity() {

    private lateinit var binding: ActivityEventoDetalleBinding
    private lateinit var sessionManager: SessionManager

    private var miReaccionActual: String? = null
    private var miEmojiActual: String = "👍"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityEventoDetalleBinding.inflate(layoutInflater)
        setContentView(binding.root)

        sessionManager = SessionManager(this)

        // TOOLBAR
        setSupportActionBar(binding.toolbarEvento)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = ""
        binding.toolbarEvento.setNavigationOnClickListener { finish() }

        // DATOS
        val eventoId = intent.getIntExtra("eventoId", 0)
        val titulo = intent.getStringExtra("titulo")
        val descripcion = intent.getStringExtra("descripcion")
        val fechaEvento = intent.getStringExtra("fechaEvento")
        val fechaPublicacion = intent.getStringExtra("fechaPublicacion")
        val estado = intent.getStringExtra("estado")
        val autorNombre = intent.getStringExtra("autorNombre")
        val autorFoto = intent.getStringExtra("autorFoto")
        val categoriaId = intent.getIntExtra("categoria", 0) 
        val multimedia = intent.getSerializableExtra("multimedia") as? ArrayList<Multimedia> ?: arrayListOf()

        // UI INICIAL
        binding.txtTituloEventoDetalle.text = titulo
        binding.txtDescripcionEvento.text = descripcion
        binding.txtAutorEvento.text = autorNombre ?: "Administrador Zapotal"
        binding.txtEstadoEvento.text = estado?.uppercase() ?: "ACTIVO"
        
        binding.txtCategoriaEvento.text = when(categoriaId) {
            1 -> "Cultural"
            2 -> "Deportivo"
            3 -> "Religioso"
            4 -> "Social"
            else -> "General"
        }

        actualizarUIReaccion()

        Glide.with(this)
            .load(autorFoto)
            .placeholder(R.drawable.ic_profile)
            .error(R.drawable.ic_profile)
            .circleCrop()
            .into(binding.imgAutorEvento)

        formatearFechas(fechaPublicacion, fechaEvento)
        setupMultimedia(multimedia)

        // LÓGICA DE REACCIONES (Tipo Facebook)
        binding.btnLikeEvento.setOnClickListener {
            if (!sessionManager.isLoggedIn()) {
                showAuthRequiredSheet()
                return@setOnClickListener
            }
            val usuarioId = sessionManager.getUserId().toInt()
            if (miReaccionActual == null) {
                enviarReaccion("LIKE", "👍", usuarioId, eventoId)
            } else {
                enviarReaccion(miReaccionActual!!, miEmojiActual, usuarioId, eventoId)
            }
        }

        binding.btnLikeEvento.setOnLongClickListener {
            if (!sessionManager.isLoggedIn()) {
                showAuthRequiredSheet()
                return@setOnLongClickListener true
            }
            // Aquí deberías tener un layout_reacciones en activity_evento_detalle.xml
            // Si no está, lo ideal es añadirlo. Por ahora asumo que existe o se añade.
            // binding.layoutReaccionesEvento.visibility = if (binding.layoutReaccionesEvento.visibility == View.VISIBLE) View.GONE else View.VISIBLE
            true
        }

        // COMENTARIOS
        binding.btnComentariosEvento.setOnClickListener {
            if (!sessionManager.isLoggedIn()) {
                showAuthRequiredSheet()
            } else {
                val bottomSheet = ComentariosBottomSheetFragment.newInstance(eventoId = eventoId)
                bottomSheet.show(supportFragmentManager, ComentariosBottomSheetFragment.TAG)
            }
        }

        // COMPARTIR
        binding.btnCompartirEvento.setOnClickListener {
            compartirEvento(titulo, descripcion)
        }
    }

    private fun showAuthRequiredSheet() {
        val authSheet = AuthRequiredBottomSheetFragment()
        authSheet.show(supportFragmentManager, AuthRequiredBottomSheetFragment.TAG)
    }

    private fun enviarReaccion(tipo: String, emoji: String, usuarioId: Int, eventoId: Int) {
        lifecycleScope.launch {
            try {
                val reaccion = ReaccionRequest(tipo = tipo, usuario = usuarioId, evento = eventoId)
                val response = RetrofitClient.apiService.crearReaccion(reaccion)

                if (response.isSuccessful) {
                    val body = response.body()
                    when (body?.accion) {
                        "creada", "actualizada" -> {
                            miReaccionActual = tipo
                            miEmojiActual = emoji
                            actualizarUIReaccion()
                        }
                        "eliminada" -> {
                            miReaccionActual = null
                            miEmojiActual = "👍"
                            actualizarUIReaccion()
                        }
                    }
                }
            } catch (e: Exception) {
                Toast.makeText(this@EventoDetalleActivity, "Error de conexión", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun actualizarUIReaccion() {
        // Asumiendo que tienes txtEmojiEvento en el XML
        // binding.txtEmojiEvento.text = miEmojiActual
        if (miReaccionActual != null) {
            binding.btnLikeEvento.setCardBackgroundColor(Color.parseColor("#10B981"))
            binding.txtLikeCountEvento.setTextColor(Color.WHITE)
        } else {
            binding.btnLikeEvento.setCardBackgroundColor(Color.parseColor("#111111"))
            binding.txtLikeCountEvento.setTextColor(Color.parseColor("#9CA3AF"))
        }
    }

    private fun formatearFechas(fechaPublicacion: String?, fechaEvento: String?) {
        try {
            val fechaLimpia = fechaPublicacion?.replace("Z", "")?.split(".")?.get(0) ?: ""
            val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val outputFormat = SimpleDateFormat("dd 'de' MMMM, yyyy", Locale("es", "ES"))
            inputFormat.parse(fechaLimpia)?.let {
                binding.txtFechaEventoPublicacion.text = outputFormat.format(it)
                
                val timeFormat = SimpleDateFormat("hh:mm a", Locale("es", "ES"))
                binding.txtHoraEvento.text = timeFormat.format(it)
            }
        } catch (e: Exception) {
            binding.txtFechaEventoPublicacion.text = fechaPublicacion ?: ""
        }

        try {
            val inputFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            val outputFormat = SimpleDateFormat("dd 'de' MMMM 'de' yyyy", Locale("es", "ES"))
            inputFormat.parse(fechaEvento ?: "")?.let {
                binding.txtFechaEventoInfo.text = outputFormat.format(it)
            }
        } catch (e: Exception) {
            binding.txtFechaEventoInfo.text = fechaEvento ?: ""
        }
    }

    private fun setupMultimedia(multimedia: List<Multimedia>) {
        if (multimedia.isNotEmpty()) {
            binding.cardMultimedia.visibility = View.VISIBLE
            binding.viewPagerEvento.adapter = MultimediaDetalleAdapter(multimedia)
            if (multimedia.size > 1) {
                binding.tabLayoutDots.visibility = View.VISIBLE
                TabLayoutMediator(binding.tabLayoutDots, binding.viewPagerEvento) { _, _ -> }.attach()
            }
        } else {
            binding.cardMultimedia.visibility = View.GONE
        }
    }

    private fun compartirEvento(titulo: String?, descripcion: String?) {
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
}
