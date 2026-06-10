package com.comunidad.zapotal.app.ui.home

import android.app.Dialog
import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.view.Window
import android.widget.ImageButton
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.viewpager2.widget.CompositePageTransformer
import androidx.viewpager2.widget.MarginPageTransformer
import androidx.viewpager2.widget.ViewPager2
import com.comunidad.zapotal.app.R
import com.comunidad.zapotal.app.adapter.NoticiaAdapter
import com.comunidad.zapotal.app.adapter.EventoAdapter
import com.comunidad.zapotal.app.adapter.ImagenAdapter
import com.comunidad.zapotal.app.adapter.AutoridadAdapter
import com.comunidad.zapotal.app.adapter.BannerItem
import com.comunidad.zapotal.app.databinding.FragmentHomeBinding
import com.comunidad.zapotal.app.data.model.Noticia
import com.comunidad.zapotal.app.data.model.Evento
import com.comunidad.zapotal.app.data.model.Autoridad
import com.comunidad.zapotal.app.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import kotlin.math.abs

class HomeFragment : Fragment(R.layout.fragment_home) {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    private val sliderHandler = Handler(Looper.getMainLooper())
    private val sliderRunnable = Runnable {
        val currentItem = binding.viewPagerDestacados.currentItem
        val adapter = binding.viewPagerDestacados.adapter
        if (adapter != null && adapter.itemCount > 0) {
            binding.viewPagerDestacados.currentItem = (currentItem + 1) % adapter.itemCount
        }
    }

    private var listaNoticias: List<Noticia> = emptyList()
    private var listaEventos: List<Evento> = emptyList()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentHomeBinding.bind(view)

        setupRecyclerViews()
        setupViewPager()
        
        binding.imgLogoApp.setOnClickListener {
            mostrarDialogoEmblema()
        }

        binding.btnVerUbicacion.setOnClickListener {
            abrirGoogleMaps()
        }

        obtenerNoticias()
        obtenerEventos()
        obtenerAutoridades()
    }

    private fun abrirGoogleMaps() {
        try {
            val query = getString(R.string.location_query)
            val intentUri = Uri.parse(query)
            val mapIntent = Intent(Intent.ACTION_VIEW, intentUri)
            // Intentamos abrir específicamente con Google Maps si está disponible
            mapIntent.setPackage("com.google.android.apps.maps")
            
            if (mapIntent.resolveActivity(requireActivity().packageManager) != null) {
                startActivity(mapIntent)
            } else {
                // Si no está la app de Maps, intentamos un intent genérico
                val genericMapIntent = Intent(Intent.ACTION_VIEW, intentUri)
                startActivity(genericMapIntent)
            }
        } catch (e: Exception) {
            Toast.makeText(requireContext(), "No se pudo abrir el mapa", Toast.LENGTH_SHORT).show()
        }
    }

    private fun mostrarDialogoEmblema() {
        val dialog = Dialog(requireContext())
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(R.layout.dialog_emblema)
        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        dialog.window?.setLayout(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT)

        val btnClose = dialog.findViewById<ImageButton>(R.id.btnClose)
        btnClose.setOnClickListener {
            dialog.dismiss()
        }

        dialog.show()
    }

    private fun setupRecyclerViews() {
        binding.recyclerNoticias.layoutManager =
            LinearLayoutManager(requireContext(), LinearLayoutManager.HORIZONTAL, false)

        binding.recyclerEventos.layoutManager =
            LinearLayoutManager(requireContext(), LinearLayoutManager.HORIZONTAL, false)
            
        binding.recyclerAutoridades.layoutManager =
            LinearLayoutManager(requireContext(), LinearLayoutManager.HORIZONTAL, false)
    }

    private fun setupViewPager() {
        val transformer = CompositePageTransformer()
        transformer.addTransformer(MarginPageTransformer(40))
        transformer.addTransformer { page, position ->
            val r = 1 - abs(position)
            page.scaleY = 0.85f + r * 0.15f
        }

        binding.viewPagerDestacados.apply {
            clipToPadding = false
            clipChildren = false
            offscreenPageLimit = 3
            setPageTransformer(transformer)
            
            registerOnPageChangeCallback(object : ViewPager2.OnPageChangeCallback() {
                override fun onPageSelected(position: Int) {
                    super.onPageSelected(position)
                    actualizarIndicadores(position)
                    sliderHandler.removeCallbacks(sliderRunnable)
                    sliderHandler.postDelayed(sliderRunnable, 3000)
                }
            })
        }
    }

    private fun setupIndicadores(count: Int) {
        binding.layoutIndicadores.removeAllViews()
        val indicators = arrayOfNulls<ImageView>(count)
        val layoutParams: LinearLayout.LayoutParams =
            LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        layoutParams.setMargins(8, 0, 8, 0)
        
        for (i in indicators.indices) {
            indicators[i] = ImageView(requireContext())
            indicators[i]?.apply {
                setImageDrawable(ContextCompat.getDrawable(requireContext(), R.drawable.dot_indicator))
                this.layoutParams = layoutParams
            }
            binding.layoutIndicadores.addView(indicators[i])
        }
        actualizarIndicadores(0)
    }

    private fun actualizarIndicadores(position: Int) {
        val childCount = binding.layoutIndicadores.childCount
        for (i in 0 until childCount) {
            val imageView = binding.layoutIndicadores.getChildAt(i) as ImageView
            imageView.isSelected = (i == position)
        }
    }

    private fun obtenerNoticias() {
        RetrofitClient.apiService.obtenerNoticias()
            .enqueue(object : Callback<List<Noticia>> {
                override fun onResponse(call: Call<List<Noticia>>, response: Response<List<Noticia>>) {
                    if (response.isSuccessful) {
                        listaNoticias = response.body() ?: emptyList()
                        binding.recyclerNoticias.adapter = NoticiaAdapter(listaNoticias)
                        combinarParaBanner()
                    }
                }
                override fun onFailure(call: Call<List<Noticia>>, t: Throwable) {
                    t.printStackTrace()
                }
            })
    }

    private fun obtenerEventos() {
        RetrofitClient.apiService.obtenerEventos().enqueue(object : Callback<List<Evento>> {
            override fun onResponse(call: Call<List<Evento>>, response: Response<List<Evento>>) {
                if (response.isSuccessful) {
                    listaEventos = response.body() ?: emptyList()
                    binding.recyclerEventos.adapter = EventoAdapter(listaEventos.toMutableList()) { _ -> }
                    combinarParaBanner()
                }
            }
            override fun onFailure(call: Call<List<Evento>>, t: Throwable) {
                t.printStackTrace()
            }
        })
    }
    
    private fun obtenerAutoridades() {
        RetrofitClient.apiService.obtenerAutoridades().enqueue(object : Callback<List<Autoridad>> {
            override fun onResponse(call: Call<List<Autoridad>>, response: Response<List<Autoridad>>) {
                if (response.isSuccessful) {
                    val autoridades = response.body() ?: emptyList()
                    binding.recyclerAutoridades.adapter = AutoridadAdapter(autoridades)
                }
            }
            override fun onFailure(call: Call<List<Autoridad>>, t: Throwable) {
                t.printStackTrace()
            }
        })
    }

    private fun combinarParaBanner() {
        val bannerItems = mutableListOf<BannerItem>()

        listaNoticias.forEach { noticia ->
            noticia.multimedia.forEach { bannerItems.add(BannerItem(it, noticia.titulo, "NOTICIA")) }
        }

        listaEventos.forEach { evento ->
            evento.multimedia.forEach { bannerItems.add(BannerItem(it, evento.titulo ?: "Evento", "EVENTO")) }
        }

        val finalItems = bannerItems.shuffled().take(8)
        if (finalItems.isNotEmpty()) {
            binding.viewPagerDestacados.adapter = ImagenAdapter(finalItems)
            setupIndicadores(finalItems.size)
        }
    }

    override fun onPause() {
        super.onPause()
        sliderHandler.removeCallbacks(sliderRunnable)
    }

    override fun onResume() {
        super.onResume()
        sliderHandler.postDelayed(sliderRunnable, 3000)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        sliderHandler.removeCallbacks(sliderRunnable)
        _binding = null
    }
}
