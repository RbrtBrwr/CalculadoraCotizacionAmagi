﻿/// La informacion de los ongoings de cada uno de los tipos?

using System;
namespace CalculadoraPianoPiano.Shared
{
    public class Ongoing
    {
        public string Tipo { get; set; }
        public List<Servicio> ListaServicio { get; set; }
    
        public Ongoing()
		{
		}
	}
}

