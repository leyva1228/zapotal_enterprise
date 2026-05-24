package com.comunidad_zapotal.comunidad_zapotal.ui.autoridades

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.bumptech.glide.Glide
import com.comunidad_zapotal.comunidad_zapotal.R
import com.comunidad_zapotal.comunidad_zapotal.databinding.ActivityAutoridadDetalleBinding

class AutoridadDetalleActivity : AppCompatActivity() {

    private lateinit var binding: ActivityAutoridadDetalleBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityAutoridadDetalleBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Configurar Toolbar
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = ""
        binding.toolbar.setNavigationOnClickListener { onBackPressedDispatcher.onBackPressed() }

        // Recibir datos
        val nombre = intent.getStringExtra("nombre")
        val cargo = intent.getStringExtra("cargo")
        val descripcion = intent.getStringExtra("descripcion")
        val fotoUrl = intent.getStringExtra("foto_url")
        val correo = intent.getStringExtra("correo")
        val telefono = intent.getStringExtra("telefono")

        // Poblar vistas
        binding.txtNombreDetalle.text = nombre
        binding.txtCargoDetalle.text = cargo
        binding.txtDescripcionDetalle.text = descripcion ?: "Sin descripción disponible."

        Glide.with(this)
            .load(fotoUrl)
            .placeholder(R.drawable.ic_profile)
            .error(R.drawable.ic_profile)
            .into(binding.imgAutoridadDetalle)

        // Listeners de botones de contacto
        binding.btnGmail.setOnClickListener {
            if (!correo.isNullOrEmpty()) {
                val intent = Intent(Intent.ACTION_SENDTO).apply {
                    data = Uri.parse("mailto:$correo")
                }
                startActivity(Intent.createChooser(intent, "Enviar correo"))
            } else {
                Toast.makeText(this, "Correo no disponible", Toast.LENGTH_SHORT).show()
            }
        }

        binding.btnWhatsApp.setOnClickListener {
            if (!telefono.isNullOrEmpty()) {
                try {
                    val url = "https://api.whatsapp.com/send?phone=$telefono"
                    val i = Intent(Intent.ACTION_VIEW)
                    i.data = Uri.parse(url)
                    startActivity(i)
                } catch (e: Exception) {
                    Toast.makeText(this, "WhatsApp no instalado", Toast.LENGTH_SHORT).show()
                }
            } else {
                Toast.makeText(this, "Teléfono no disponible", Toast.LENGTH_SHORT).show()
            }
        }

        binding.btnPhone.setOnClickListener {
            if (!telefono.isNullOrEmpty()) {
                val intent = Intent(Intent.ACTION_DIAL).apply {
                    data = Uri.parse("tel:$telefono")
                }
                startActivity(intent)
            } else {
                Toast.makeText(this, "Teléfono no disponible", Toast.LENGTH_SHORT).show()
            }
        }
    }
}