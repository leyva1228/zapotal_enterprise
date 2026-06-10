package com.comunidad.zapotal.app.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.comunidad.zapotal.app.R
import com.comunidad.zapotal.app.data.model.Comentario
import com.comunidad.zapotal.app.databinding.ItemComentarioBinding

class ComentariosAdapter(private val comentarios: List<Comentario>) :
    RecyclerView.Adapter<ComentariosAdapter.ComentarioViewHolder>() {

    class ComentarioViewHolder(val binding: ItemComentarioBinding) :
        RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ComentarioViewHolder {
        val binding = ItemComentarioBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ComentarioViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ComentarioViewHolder, position: Int) {
        val comentario = comentarios[position]
        with(holder.binding) {
            txtNombreUserComentario.text = "${comentario.usuario.nombres} ${comentario.usuario.apellidos}"
            txtContenidoComentario.text = comentario.contenido
            txtTiempoComentario.text = comentario.fecha

            Glide.with(imgUserComentario.context)
                .load(comentario.usuario.foto_perfil_url)
                .placeholder(R.drawable.ic_profile)
                .error(R.drawable.ic_profile)
                .circleCrop()
                .into(imgUserComentario)
        }
    }

    override fun getItemCount() = comentarios.size
}
