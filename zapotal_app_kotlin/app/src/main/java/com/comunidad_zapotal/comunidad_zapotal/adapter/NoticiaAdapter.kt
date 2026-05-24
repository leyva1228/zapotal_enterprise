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

class NoticiaAdapter(
    private val lista: List<Noticia>
) : RecyclerView.Adapter<NoticiaAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imagen: ImageView = view.findViewById(R.id.imgNoticia)
        val titulo: TextView = view.findViewById(R.id.txtTitulo)
        val publicado: TextView = view.findViewById(R.id.txtPublicadoEl)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_noticia, parent, false)
        return ViewHolder(view)
    }

    override fun getItemCount(): Int = lista.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val noticia = lista[position]
        holder.titulo.text = noticia.titulo

        // Formatear fecha de publicación
        try {
            val formatoEntrada = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val fechaDate = formatoEntrada.parse(noticia.fecha_publicacion)
            val formatoSalida = SimpleDateFormat("dd MMM yyyy", Locale("es", "ES"))
            holder.publicado.text = "Publicado el ${formatoSalida.format(fechaDate!!)}"
        } catch (e: Exception) {
            holder.publicado.text = "Publicado el ${noticia.fecha_publicacion}"
        }

        if (noticia.multimedia.isNotEmpty()) {
            Glide.with(holder.itemView.context)
                .load(noticia.multimedia[0].archivo_url)
                .placeholder(R.drawable.ic_launcher_background)
                .error(R.drawable.ic_launcher_background)
                .into(holder.imagen)
        }
    }
}