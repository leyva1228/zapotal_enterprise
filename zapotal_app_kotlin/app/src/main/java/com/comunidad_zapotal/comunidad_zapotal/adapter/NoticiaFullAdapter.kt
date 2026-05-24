package com.comunidad_zapotal.comunidad_zapotal.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.comunidad_zapotal.comunidad_zapotal.R
import com.comunidad_zapotal.comunidad_zapotal.data.model.Noticia
import java.text.SimpleDateFormat
import java.util.Locale

class NoticiaFullAdapter(
    private var lista: List<Noticia>,
    private val onDetalleClick: (Noticia) -> Unit
) : RecyclerView.Adapter<NoticiaFullAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imagen: ImageView = view.findViewById(R.id.imgNoticia)
        val titulo: TextView = view.findViewById(R.id.txtTitulo)
        val contenido: TextView = view.findViewById(R.id.txtContenido)
        val publicado: TextView = view.findViewById(R.id.txtPublicadoEl)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_noticia_vertical, parent, false)
        return ViewHolder(view)
    }

    override fun getItemCount(): Int = lista.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val noticia = lista[position]
        holder.titulo.text = noticia.titulo
        holder.contenido.text = noticia.contenido

        // Formatear fecha de publicación: "Publicado el 11 mayo 2026"
        try {
            val formatoEntrada = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val fechaDate = formatoEntrada.parse(noticia.fecha_publicacion ?: "")
            val formatoSalida = SimpleDateFormat("dd MMMM yyyy", Locale("es", "ES"))
            holder.publicado.text = "Publicado el ${formatoSalida.format(fechaDate!!)}"
        } catch (e: Exception) {
            holder.publicado.text = noticia.fecha_publicacion
        }

        if (noticia.multimedia.isNotEmpty()) {
            Glide.with(holder.itemView.context)
                .load(noticia.multimedia[0].archivo_url)
                .placeholder(R.drawable.ic_launcher_background)
                .error(R.drawable.ic_launcher_background)
                .into(holder.imagen)
        } else {
            holder.imagen.setImageResource(R.drawable.ic_launcher_background)
        }

        holder.itemView.setOnClickListener { onDetalleClick(noticia) }
    }

    fun updateList(nuevaLista: List<Noticia>) {
        lista = nuevaLista
        notifyDataSetChanged()
    }
}