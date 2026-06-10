package com.comunidad.zapotal.app.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.comunidad.zapotal.app.R
import com.comunidad.zapotal.app.data.model.Multimedia

data class BannerItem(
    val multimedia: Multimedia,
    val titulo: String,
    val categoria: String
)

class ImagenAdapter(
    private val listaBanner: List<BannerItem>
) : RecyclerView.Adapter<ImagenAdapter.ImagenViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ImagenViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_imagen, parent, false)
        return ImagenViewHolder(view)
    }

    override fun onBindViewHolder(holder: ImagenViewHolder, position: Int) {
        val item = listaBanner[position]

        holder.txtTitulo.text = item.titulo
        holder.txtCategoria.text = item.categoria

        // Cambiar el color del fondo de la categoría según sea Noticia o Evento
        if (item.categoria == "EVENTO") {
            holder.txtCategoria.setBackgroundResource(R.drawable.bg_tag_evento)
        } else {
            holder.txtCategoria.setBackgroundResource(R.drawable.bg_tag_noticia)
        }

        Glide.with(holder.itemView.context)
            .load(item.multimedia.archivo_url)
            .placeholder(R.drawable.ic_launcher_background)
            .error(R.drawable.ic_launcher_background)
            .centerCrop()
            .into(holder.imgBanner)
    }

    override fun getItemCount(): Int = listaBanner.size

    class ImagenViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imgBanner: ImageView = view.findViewById(R.id.imgBanner)
        val txtTitulo: TextView = view.findViewById(R.id.txtTituloBanner)
        val txtCategoria: TextView = view.findViewById(R.id.txtCategoriaBanner)
    }
}