package com.comunidad.zapotal.app.ui.perfil

import android.os.Bundle
import android.widget.ImageButton
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.comunidad.zapotal.app.R
import com.comunidad.zapotal.app.data.model.Usuario
import com.comunidad.zapotal.app.utils.SessionManager
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText

class EditarPerfilActivity : AppCompatActivity() {

    private lateinit var sessionManager: SessionManager
    private lateinit var etNombres: TextInputEditText
    private lateinit var etApellidos: TextInputEditText
    private lateinit var etEmail: TextInputEditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_editar_perfil)

        sessionManager = SessionManager(this)

        etNombres = findViewById(R.id.etNombresEditar)
        etApellidos = findViewById(R.id.etApellidosEditar)
        etEmail = findViewById(R.id.etEmailEditar)

        findViewById<ImageButton>(R.id.btnBackEditar).setOnClickListener { finish() }

        cargarDatosActuales()

        findViewById<MaterialButton>(R.id.btnGuardarPerfil).setOnClickListener {
            guardarCambios()
        }
    }

    private fun cargarDatosActuales() {
        sessionManager.getUser()?.let {
            etNombres.setText(it.nombres)
            etApellidos.setText(it.apellidos)
            etEmail.setText(it.email)
        }
    }

    private fun guardarCambios() {
        val nombres = etNombres.text.toString().trim()
        val apellidos = etApellidos.text.toString().trim()
        val email = etEmail.text.toString().trim()

        if (nombres.isEmpty() || apellidos.isEmpty() || email.isEmpty()) {
            Toast.makeText(this, "Por favor complete todos los campos", Toast.LENGTH_SHORT).show()
            return
        }

        val usuarioActual = sessionManager.getUser() ?: return
        val usuarioActualizado = usuarioActual.copy(
            nombres = nombres,
            apellidos = apellidos,
            email = email
        )

        // Nota: Aquí se debería llamar al API para persistir en el servidor
        // Por ahora actualizamos la sesión local para que se refleje en toda la app
        sessionManager.saveUser(usuarioActualizado)
        Toast.makeText(this, "Perfil actualizado con éxito", Toast.LENGTH_SHORT).show()
        finish()
    }
}
