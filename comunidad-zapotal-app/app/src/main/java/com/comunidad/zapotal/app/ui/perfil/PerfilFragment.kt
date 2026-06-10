package com.comunidad.zapotal.app.ui.perfil

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.bumptech.glide.Glide
import com.comunidad.zapotal.app.MainActivity
import com.comunidad.zapotal.app.R
import com.comunidad.zapotal.app.databinding.FragmentPerfilBinding
import com.comunidad.zapotal.app.ui.auth.LoginActivity
import com.comunidad.zapotal.app.ui.auth.RegisterActivity
import com.comunidad.zapotal.app.utils.SessionManager

class PerfilFragment : Fragment(R.layout.fragment_perfil) {

    private var _binding: FragmentPerfilBinding? = null
    private val binding get() = _binding!!
    private lateinit var sessionManager: SessionManager

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentPerfilBinding.bind(view)
        sessionManager = SessionManager(requireContext())

        actualizarInterfaz()
        setupListeners()
    }

    private fun actualizarInterfaz() {
        if (sessionManager.isLoggedIn()) {
            binding.layoutLogged.visibility = View.VISIBLE
            binding.layoutNotLogged.visibility = View.GONE
            cargarDatosUsuario()
        } else {
            binding.layoutLogged.visibility = View.GONE
            binding.layoutNotLogged.visibility = View.VISIBLE
        }
    }

    private fun setupListeners() {
        // Botones para usuario NO logueado
        binding.btnIrLogin.setOnClickListener {
            startActivity(Intent(requireContext(), LoginActivity::class.java))
        }

        binding.btnIrRegister.setOnClickListener {
            startActivity(Intent(requireContext(), RegisterActivity::class.java))
        }

        // Opciones para usuario logueado
        binding.btnMenu.setOnClickListener {
            (activity as? MainActivity)?.openDrawer()
        }

        binding.optionInformacion.setOnClickListener {
            // ABRIMOS LA ACTIVIDAD DE INFORMACIÓN DETALLADA
            startActivity(Intent(requireContext(), InformacionUsuarioActivity::class.java))
        }

        binding.optionCerrarSesion.setOnClickListener {
            sessionManager.logout()
            Toast.makeText(requireContext(), "Sesión cerrada", Toast.LENGTH_SHORT).show()
            actualizarInterfaz()
        }

        // Otras opciones
        binding.optionReportes.setOnClickListener { Toast.makeText(requireContext(), "Mis reportes", Toast.LENGTH_SHORT).show() }
        binding.optionNotificaciones.setOnClickListener { Toast.makeText(requireContext(), "Notificaciones", Toast.LENGTH_SHORT).show() }
        binding.optionPrivacidad.setOnClickListener { Toast.makeText(requireContext(), "Privacidad", Toast.LENGTH_SHORT).show() }
        binding.optionConfiguracion.setOnClickListener { Toast.makeText(requireContext(), "Configuración", Toast.LENGTH_SHORT).show() }
        binding.optionAyuda.setOnClickListener { Toast.makeText(requireContext(), "Ayuda y soporte", Toast.LENGTH_SHORT).show() }
    }

    private fun cargarDatosUsuario() {
        val usuario = sessionManager.getUser()
        usuario?.let {
            binding.txtNombrePerfil.text = "${it.nombres} ${it.apellidos}"
            binding.txtRolPerfil.text = it.tipo_usuario
            binding.txtEstadoUsuario.text = it.estado
            
            Glide.with(this)
                .load(it.foto_perfil_url)
                .placeholder(R.drawable.ic_profile)
                .error(R.drawable.ic_profile)
                .circleCrop()
                .into(binding.imgPerfil)
        }
    }

    override fun onResume() {
        super.onResume()
        // Refrescar la interfaz por si el usuario acaba de loguearse
        actualizarInterfaz()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
