package com.comunidad.zapotal.app.ui.perfil

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.widget.ImageButton
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import com.bumptech.glide.Glide
import com.comunidad.zapotal.app.R
import com.comunidad.zapotal.app.data.model.Usuario
import com.comunidad.zapotal.app.network.RetrofitClient
import com.comunidad.zapotal.app.utils.SessionManager
import com.google.android.material.button.MaterialButton
import com.google.android.material.card.MaterialCardView
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class InformacionUsuarioActivity : AppCompatActivity() {

    private lateinit var sessionManager: SessionManager
    private lateinit var imgPerfil: ImageView

    private val pickImageLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            val imageUri: Uri? = result.data?.data
            imageUri?.let { uri ->
                // Actualizamos la vista
                Glide.with(this).load(uri).circleCrop().into(imgPerfil)
                
                // Guardamos en la sesión para que se refleje en toda la app
                val usuarioActual = sessionManager.getUser()
                usuarioActual?.let { user ->
                    val updatedUser = user.copy(foto_perfil_url = uri.toString())
                    sessionManager.saveUser(updatedUser)
                    Toast.makeText(this, "Foto de perfil actualizada", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_informacion_usuario)

        sessionManager = SessionManager(this)
        imgPerfil = findViewById(R.id.imgFotoInfo)

        findViewById<ImageButton>(R.id.btnBackInfo).setOnClickListener { finish() }

        findViewById<MaterialButton>(R.id.btnEditarPerfil).setOnClickListener {
            startActivity(Intent(this, EditarPerfilActivity::class.java))
        }

        // Click en el icono de cámara o en la misma foto para cambiarla
        findViewById<MaterialCardView>(R.id.btnChangePhoto).setOnClickListener { openGallery() }
        imgPerfil.setOnClickListener { openGallery() }

        cargarInformacion()
    }

    private fun openGallery() {
        val intent = Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)
        pickImageLauncher.launch(intent)
    }

    private fun cargarInformacion() {
        val userId = sessionManager.getUserId()
        if (userId != -1L) {
            RetrofitClient.apiService.obtenerUsuarioPorId(userId).enqueue(object : Callback<Usuario> {
                override fun onResponse(call: Call<Usuario>, response: Response<Usuario>) {
                    if (response.isSuccessful && response.body() != null) {
                        val usuario = response.body()!!
                        // No sobreescribimos la foto local si ya la cambiamos y no se ha subido al server
                        val localUser = sessionManager.getUser()
                        if (localUser?.foto_perfil_url != null && !usuario.foto_perfil_url.isNullOrEmpty()) {
                            // lógica opcional para decidir cual usar
                        }
                        sessionManager.saveUser(usuario)
                        mostrarDatos(usuario)
                    } else {
                        sessionManager.getUser()?.let { mostrarDatos(it) }
                    }
                }

                override fun onFailure(call: Call<Usuario>, t: Throwable) {
                    sessionManager.getUser()?.let { mostrarDatos(it) }
                }
            })
        }
    }

    private fun mostrarDatos(user: Usuario) {
        findViewById<TextView>(R.id.txtNombresInfo).text = user.nombres
        findViewById<TextView>(R.id.txtApellidosInfo).text = user.apellidos
        findViewById<TextView>(R.id.txtDniInfo).text = user.dni
        findViewById<TextView>(R.id.txtEmailInfo).text = user.email
        findViewById<TextView>(R.id.txtRolInfo).text = user.tipo_usuario
        findViewById<TextView>(R.id.txtFechaRegistroInfo).text = user.fecha_registro ?: "No disponible"

        Glide.with(this)
            .load(user.foto_perfil_url)
            .placeholder(R.drawable.ic_profile)
            .error(R.drawable.ic_profile)
            .circleCrop()
            .into(imgPerfil)
    }

    override fun onResume() {
        super.onResume()
        // Recargar datos por si se editó el perfil
        sessionManager.getUser()?.let { mostrarDatos(it) }
    }
}
