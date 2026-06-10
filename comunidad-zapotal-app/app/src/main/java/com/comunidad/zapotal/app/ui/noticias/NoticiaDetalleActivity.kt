package com.comunidad.zapotal.app.ui.noticias

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.bumptech.glide.Glide
import com.comunidad.zapotal.app.R
import com.comunidad.zapotal.app.adapter.MultimediaDetalleAdapter
import com.comunidad.zapotal.app.data.model.Multimedia
import com.comunidad.zapotal.app.data.model.ReaccionRequest
import com.comunidad.zapotal.app.databinding.ActivityNoticiaDetalleBinding
import com.comunidad.zapotal.app.network.RetrofitClient
import com.comunidad.zapotal.app.ui.auth.AuthRequiredBottomSheetFragment
import com.comunidad.zapotal.app.utils.SessionManager
import com.google.android.material.tabs.TabLayoutMediator
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Locale

class NoticiaDetalleActivity : AppCompatActivity() {

    private lateinit var binding: ActivityNoticiaDetalleBinding
    private lateinit var sessionManager: SessionManager

    private var minutosLeyendo = 0
    private var miReaccionActual: String? = null
    private var miEmojiActual: String = "👍"

    private val handler = Handler(Looper.getMainLooper())

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

        sessionManager = SessionManager(this)

        // TOOLBAR
        setSupportActionBar(binding.toolbarNoticia)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = ""
        binding.toolbarNoticia.setNavigationOnClickListener { finish() }

        // DATOS
        val noticiaId = intent.getIntExtra("noticiaId", 0)
        val initialLikeCount = intent.getIntExtra("likeCount", 0)
        val titulo = intent.getStringExtra("titulo")
        val contenido = intent.getStringExtra("contenido")
        val fecha = intent.getStringExtra("fecha")
        val autorNombre = intent.getStringExtra("autorNombre")
        val autorFoto = intent.getStringExtra("autorFoto")
        val estado = intent.getStringExtra("estado")
        val multimedia = intent.getSerializableExtra("multimedia") as? ArrayList<Multimedia> ?: arrayListOf()

        // UI INICIAL
        binding.txtTituloNoticiaDetalle.text = titulo
        binding.txtContenidoNoticiaDetalle.text = contenido
        binding.txtAutorNoticiaDetalle.text = autorNombre ?: "Redactor Zapotal"
        binding.txtEstadoNoticia.text = estado?.uppercase() ?: "ACTIVO"
        binding.txtLikeCountNoticia.text = initialLikeCount.toString()
        
        actualizarUIReaccion()

        Glide.with(this)
            .load(autorFoto)
            .placeholder(R.drawable.ic_profile)
            .error(R.drawable.ic_profile)
            .circleCrop()
            .into(binding.imgAutorNoticiaDetalle)

        formatearFecha(fecha)
        setupMultimedia(multimedia)
        handler.postDelayed(actualizarTiempoLectura, 60000)

        // CARGAR CONTEO REAL
        cargarConteoReacciones(noticiaId)

        // REACCIONES TIPO FACEBOOK
        binding.btnLikeNoticia.setOnClickListener {
            if (!sessionManager.isLoggedIn()) {
                showAuthRequiredSheet()
                return@setOnClickListener
            }
            
            val usuarioId = sessionManager.getUserId().toInt()
            if (miReaccionActual == null) {
                enviarReaccion("LIKE", "👍", usuarioId, noticiaId)
            } else {
                enviarReaccion(miReaccionActual!!, miEmojiActual, usuarioId, noticiaId)
            }
        }

        binding.btnLikeNoticia.setOnLongClickListener {
            if (!sessionManager.isLoggedIn()) {
                showAuthRequiredSheet()
                return@setOnLongClickListener true
            }
            binding.layoutReacciones.visibility = if (binding.layoutReacciones.visibility == View.VISIBLE) View.GONE else View.VISIBLE
            true
        }

        setupReaccionesListeners(noticiaId)

        // COMENTARIOS
        binding.btnComentariosNoticia.setOnClickListener {
            if (!sessionManager.isLoggedIn()) {
                showAuthRequiredSheet()
            } else {
                val bottomSheet = ComentariosBottomSheetFragment.newInstance(noticiaId)
                bottomSheet.show(supportFragmentManager, ComentariosBottomSheetFragment.TAG)
            }
        }

        binding.btnShareNoticia.setOnClickListener {
            compartirNoticia(titulo, contenido)
        }
    }

    private fun showAuthRequiredSheet() {
        val authSheet = AuthRequiredBottomSheetFragment()
        authSheet.show(supportFragmentManager, AuthRequiredBottomSheetFragment.TAG)
    }

    private fun setupReaccionesListeners(noticiaId: Int) {
        binding.reaccionLike.setOnClickListener { handleReactionClick("LIKE", "👍", noticiaId) }
        binding.reaccionLove.setOnClickListener { handleReactionClick("LOVE", "❤️", noticiaId) }
        binding.reaccionEnojo.setOnClickListener { handleReactionClick("ENOJO", "😡", noticiaId) }
        binding.reaccionJaja.setOnClickListener { handleReactionClick("JAJA", "😂", noticiaId) }
        binding.reaccionWow.setOnClickListener { handleReactionClick("WOW", "😮", noticiaId) }
    }

    private fun handleReactionClick(tipo: String, emoji: String, noticiaId: Int) {
        if (!sessionManager.isLoggedIn()) {
            showAuthRequiredSheet()
            return
        }
        enviarReaccion(tipo, emoji, sessionManager.getUserId().toInt(), noticiaId)
    }

    private fun enviarReaccion(tipo: String, emoji: String, usuarioId: Int, noticiaId: Int) {
        lifecycleScope.launch {
            try {
                val reaccion = ReaccionRequest(tipo = tipo, usuario = usuarioId, noticia = noticiaId)
                val response = RetrofitClient.apiService.crearReaccion(reaccion)

                if (response.isSuccessful) {
                    val body = response.body()
                    binding.layoutReacciones.visibility = View.GONE

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
                    cargarConteoReacciones(noticiaId)
                }
            } catch (e: Exception) {
                Toast.makeText(this@NoticiaDetalleActivity, "Error de conexión", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun actualizarUIReaccion() {
        binding.txtEmojiSeleccionado.text = miEmojiActual
        if (miReaccionActual != null) {
            binding.btnLikeNoticia.setCardBackgroundColor(Color.parseColor("#10B981"))
            binding.txtEmojiSeleccionado.alpha = 1.0f
            binding.txtLikeCountNoticia.setTextColor(Color.WHITE)
        } else {
            binding.btnLikeNoticia.setCardBackgroundColor(Color.parseColor("#111111"))
            binding.txtEmojiSeleccionado.alpha = 0.5f
            binding.txtLikeCountNoticia.setTextColor(Color.parseColor("#9CA3AF"))
        }
    }

    private fun cargarConteoReacciones(noticiaId: Int) {
        lifecycleScope.launch {
            try {
                val response = RetrofitClient.apiService.obtenerConteoReacciones(noticiaId)
                if (response.isSuccessful) {
                    response.body()?.let {
                        binding.txtLikeCountNoticia.text = it.total.toString()
                    }
                }
            } catch (e: Exception) { e.printStackTrace() }
        }
    }

    private fun formatearFecha(fecha: String?) {
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
    }

    private fun setupMultimedia(multimedia: List<Multimedia>) {
        if (multimedia.isNotEmpty()) {
            binding.cardMultimediaNoticia.visibility = View.VISIBLE
            binding.viewPagerNoticia.adapter = MultimediaDetalleAdapter(multimedia as ArrayList<Multimedia>)
            if (multimedia.size > 1) {
                binding.tabLayoutDotsNoticia.visibility = View.VISIBLE
                TabLayoutMediator(binding.tabLayoutDotsNoticia, binding.viewPagerNoticia) { _, _ -> }.attach()
            }
        } else {
            binding.cardMultimediaNoticia.visibility = View.GONE
        }
    }

    private fun compartirNoticia(titulo: String?, contenido: String?) {
        val intent = Intent().apply {
            action = Intent.ACTION_SEND
            putExtra(Intent.EXTRA_TEXT, "📰 $titulo\n\n$contenido\n\nComunidad Zapotal")
            type = "text/plain"
        }
        startActivity(Intent.createChooser(intent, "Compartir noticia"))
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacks(actualizarTiempoLectura)
    }
}
