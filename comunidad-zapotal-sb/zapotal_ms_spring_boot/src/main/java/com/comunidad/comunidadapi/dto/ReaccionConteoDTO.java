package com.comunidad.comunidadapi.dto;

public class ReaccionConteoDTO {

    private long likes;
    private long love;
    private long enojo;
    private long jaja;
    private long wow;
    private long total;

    public long getLikes() {
        return likes;
    }

    public void setLikes(long likes) {
        this.likes = likes;
    }

    public long getLove() {
        return love;
    }

    public void setLove(long love) {
        this.love = love;
    }

    public long getEnojo() {
        return enojo;
    }

    public void setEnojo(long enojo) {
        this.enojo = enojo;
    }

    public long getJaja() {
        return jaja;
    }

    public void setJaja(long jaja) {
        this.jaja = jaja;
    }

    public long getWow() {
        return wow;
    }

    public void setWow(long wow) {
        this.wow = wow;
    }

    public long getTotal() {
        return total;
    }

    public void setTotal(long total) {
        this.total = total;
    }
}