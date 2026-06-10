package com.comunidad.zapotal.app.ui.noticias

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.LinearLayoutManager
import com.comunidad.zapotal.app.adapter.ComentariosAdapter
import com.comunidad.zapotal.app.data.model.Comentario
import com.comunidad.zapotal.app.data.model.Usuario
import com.comunidad.zapotal.app.databinding.LayoutComentariosBottomSheetBinding
import com.google.android.material.bottomsheet.BottomSheetDialogFragment

class ComentariosBottomSheetFragment : BottomSheetDialogFragment() {

    private var _binding: LayoutComentariosBottomSheetBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = LayoutComentariosBottomSheetBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        
        binding.btnCloseComments.setOnClickListener {
            dismiss()
        }

        // Datos de prueba para mostrar el diseño
        mostrarComentariosPrueba()
    }

    private fun setupRecyclerView() {
        binding.recyclerComentarios.layoutManager = LinearLayoutManager(requireContext())
    }

    private fun mostrarComentariosPrueba() {
        val usuarioPrueba = Usuario(
            id = 1,
            nombres = "Andrés",
            apellidos = "López",
            email = "andres@gmail.com",
            dni = "12345678",
            telefono = null,
            tipo_usuario = "USER",
            estado = "ACTIVO",
            dni_verificado = true,
            foto_perfil_url = null,
            fecha_registro = null
        )

        val listaPrueba = listOf(
            Comentario(1, "¡Qué tierno! 😍", "2 h", usuarioPrueba),
            Comentario(2, "Me alegró el día este video 🐶", "3 h", usuarioPrueba),
            Comentario(3, "Hermoso perrito ❤️", "5 h", usuarioPrueba),
            Comentario(4, "Amo los golden 🥺", "8 h", usuarioPrueba)
        )

        binding.recyclerComentarios.adapter = ComentariosAdapter(listaPrueba)
        binding.txtCountComentarios.text = "${listaPrueba.size} comentarios"
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    companion object {
        const val TAG = "ComentariosBottomSheet"
        
        fun newInstance(noticiaId: Int? = null, eventoId: Int? = null) = ComentariosBottomSheetFragment().apply {
            arguments = Bundle().apply {
                if (noticiaId != null) putInt("noticiaId", noticiaId)
                if (eventoId != null) putInt("eventoId", eventoId)
            }
        }
    }
}
