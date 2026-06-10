package com.comunidad.zapotal.app.ui.autoridades

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.appcompat.widget.SearchView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import com.comunidad.zapotal.app.R
import com.comunidad.zapotal.app.adapter.AutoridadFullAdapter
import com.comunidad.zapotal.app.data.model.Autoridad
import com.comunidad.zapotal.app.databinding.FragmentAutoridadesBinding
import com.comunidad.zapotal.app.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class AutoridadesFragment : Fragment(R.layout.fragment_autoridades) {

    private var _binding: FragmentAutoridadesBinding? = null
    private val binding get() = _binding!!

    private lateinit var adapter: AutoridadFullAdapter
    private var listaOriginal: List<Autoridad> = emptyList()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentAutoridadesBinding.bind(view)

        setupRecyclerView()
        setupSearchView()
        obtenerAutoridades()
    }

    private fun setupRecyclerView() {
        adapter = AutoridadFullAdapter(emptyList()) { autoridad ->
            abrirDetalleAutoridad(autoridad)
        }
        binding.recyclerAutoridadesFull.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerAutoridadesFull.adapter = adapter
    }

    private fun setupSearchView() {
        binding.searchViewAutoridades.setOnQueryTextListener(object : SearchView.OnQueryTextListener {
            override fun onQueryTextSubmit(query: String?): Boolean = false
            override fun onQueryTextChange(newText: String?): Boolean {
                filtrarPorCargo(newText ?: "")
                return true
            }
        })
    }

    private fun filtrarPorCargo(query: String) {
        val listaFiltrada = if (query.isEmpty()) {
            listaOriginal
        } else {
            listaOriginal.filter { 
                it.cargo?.lowercase()?.contains(query.lowercase()) == true 
            }
        }
        
        actualizarVistaEmpty(listaFiltrada)
        adapter.updateList(listaFiltrada)
    }

    private fun actualizarVistaEmpty(lista: List<Autoridad>) {
        if (lista.isEmpty()) {
            binding.layoutEmptyAutoridades.visibility = View.VISIBLE
            binding.recyclerAutoridadesFull.visibility = View.GONE
        } else {
            binding.layoutEmptyAutoridades.visibility = View.GONE
            binding.recyclerAutoridadesFull.visibility = View.VISIBLE
        }
    }

    private fun obtenerAutoridades() {
        RetrofitClient.apiService.obtenerAutoridades().enqueue(object : Callback<List<Autoridad>> {
            override fun onResponse(
                call: Call<List<Autoridad>>,
                response: Response<List<Autoridad>>
            ) {
                if (response.isSuccessful) {
                    listaOriginal = response.body() ?: emptyList()
                    actualizarVistaEmpty(listaOriginal)
                    adapter.updateList(listaOriginal)
                }
            }

            override fun onFailure(call: Call<List<Autoridad>>, t: Throwable) {
                t.printStackTrace()
            }
        })
    }

    private fun abrirDetalleAutoridad(autoridad: Autoridad) {
        val intent = Intent(requireContext(), AutoridadDetalleActivity::class.java).apply {
            putExtra("nombre", "${autoridad.nombres} ${autoridad.apellidos}")
            putExtra("cargo", autoridad.cargo)
            putExtra("descripcion", autoridad.descripcion)
            putExtra("foto_url", autoridad.foto_url)
            putExtra("correo", autoridad.correo)
            putExtra("telefono", autoridad.telefono)
        }
        startActivity(intent)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}