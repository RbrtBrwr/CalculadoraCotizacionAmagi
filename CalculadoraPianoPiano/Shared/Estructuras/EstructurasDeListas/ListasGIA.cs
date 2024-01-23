using System;
using CalculadoraPianoPiano.Shared;
namespace CalculadoraPianoPiano.Shared.Estructuras.EstructurasDeListas
{
    public class ListasGIA
    {
        public ListasTIC ListasTIC { get; set; }
        public ListasPMO ListasPMO { get; set; }
        public ListasIoT ListasIoT { get; set; }
        public ListasCiberSeguridad ListasCiberSeguridad { get; set; }

        public ListasGIA()
        {
            ListasTIC = new ListasTIC();
            ListasPMO = new ListasPMO();
            ListasIoT = new ListasIoT();
            ListasCiberSeguridad = new ListasCiberSeguridad();
        }
    }
}