package com.comunidad.zapotal.app.ui.auth

import android.content.Intent
import android.os.Bundle
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.comunidad.zapotal.app.MainActivity
import com.comunidad.zapotal.app.R
import com.comunidad.zapotal.app.data.model.LoginRequest
import com.comunidad.zapotal.app.data.model.LoginResponse
import com.comunidad.zapotal.app.network.RetrofitClient
import com.comunidad.zapotal.app.utils.SessionManager
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class LoginActivity : AppCompatActivity() {

    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        sessionManager = SessionManager(this)

        val btnBack = findViewById<ImageButton>(R.id.btnBackLogin)
        val etEmail = findViewById<TextInputEditText>(R.id.etEmail)
        val etPassword = findViewById<TextInputEditText>(R.id.etPassword)
        val btnLogin = findViewById<MaterialButton>(R.id.btnLogin)
        val btnIrRegistro = findViewById<TextView>(R.id.btnIrRegistro)
        val btnGoogle = findViewById<MaterialButton>(R.id.btnGoogle)
        val btnForgotPassword = findViewById<TextView>(R.id.btnForgotPassword)

        btnBack.setOnClickListener { finish() }

        btnIrRegistro.setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }

        btnForgotPassword.setOnClickListener {
            startActivity(Intent(this, ForgotPasswordActivity::class.java))
        }

        btnLogin.setOnClickListener {
            val email = etEmail.text.toString().trim()
            val password = etPassword.text.toString().trim()

            if (email.isEmpty() || password.isEmpty()) {
                Toast.makeText(this, "Ingresa tus credenciales", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val request = LoginRequest(email = email, password = password)

            RetrofitClient.apiService.login(request).enqueue(object : Callback<LoginResponse> {
                override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>) {
                    if (response.isSuccessful) {
                        val loginResponse = response.body()
                        if (loginResponse?.ok == true && loginResponse.usuario != null) {
                            sessionManager.saveUser(loginResponse.usuario)
                            Toast.makeText(this@LoginActivity, loginResponse.mensaje, Toast.LENGTH_SHORT).show()
                            
                            val intent = Intent(this@LoginActivity, MainActivity::class.java)
                            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                            startActivity(intent)
                        } else {
                            Toast.makeText(this@LoginActivity, loginResponse?.mensaje ?: "Credenciales incorrectas", Toast.LENGTH_SHORT).show()
                        }
                    } else {
                        Toast.makeText(this@LoginActivity, "Usuario o contraseña incorrectos", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                    Toast.makeText(this@LoginActivity, "Sin conexión al servidor", Toast.LENGTH_LONG).show()
                }
            })
        }

        btnGoogle.setOnClickListener {
            Toast.makeText(this, "Próximamente: Inicio con Google", Toast.LENGTH_SHORT).show()
        }
    }
}
