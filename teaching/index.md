---
title: Teaching & supervision
description: Teaching in numerical methods, computational fluid dynamics and high-performance computing, with MSc research topics.
---
<header class="page-intro"><p class="overline">Teaching & supervision</p><h1>From numerical ideas<br>to working simulations.</h1><p>My teaching brings together numerical analysis, fluid physics and scientific software, connecting mathematical understanding with practical simulation.</p></header>

<div class="prose" markdown="1">

## Subjects and approach

My teaching has covered the foundations of CFD and their application to engineering flows:

- **Numerical methods for compressible flows:** conservation laws, hyperbolic systems, shock formation, Riemann solvers, high-order reconstruction and time integration.
- **Numerical methods for partial differential equations:** finite-difference, finite-volume and finite-element approaches; stability, convergence, and numerical dissipation and dispersion.
- **High-performance computing:** parallel programming with MPI and OpenMP, mesh partitioning, and practical implementation in Fortran and Python.
- **Turbulence modelling:** RANS closures, large-eddy simulation, direct numerical simulation, and the interpretation and assessment of turbulent-flow predictions.
- **Mesh generation and simulation practice:** structured and unstructured meshes, boundary conditions, verification, validation and post-processing.
- **CFD applications:** aeronautical, automotive and environmental flows, fluid–structure interaction, multiphase flows and combustion.

Practical work asks students to implement numerical methods, compare their behaviour on test problems, and explain the relationship between computational choices and the resulting flow predictions. Research projects extend this approach to open questions in methods, flow physics and scientific computing.

I am a Fellow of the Higher Education Academy and hold a postgraduate certificate in Academic Practice in Higher Education.

## Research supervision

My supervision spans numerical methods and applications in CFD, including high-speed aerodynamics, turbulence, multiphase flows and high-performance computing. Research supervisees and alumni are listed on the [people page]({{ '/people/' | relative_url }}).

</div>

<section class="section" aria-labelledby="msc-topics-heading">
  <div class="section-heading"><div><p class="overline">MSc supervision</p><h2 id="msc-topics-heading">Research topics</h2></div></div>
  <p>Topics from individual and group MSc research projects, organised by academic year.</p>
  {% assign topic_years = site.data.msc_topics | group_by: 'year' | sort: 'name' | reverse %}
  <div class="msc-topic-years">
  {% for topic_year in topic_years %}
    <details class="msc-topic-year">
      <summary>{{ topic_year.name | escape }} <span class="quiet">· {{ topic_year.items.size }} topics</span></summary>
      <ul class="msc-topic-list">
      {% for item in topic_year.items %}
        <li><p><strong>{{ item.topic | escape }}</strong><br><span class="quiet">{{ item.course | escape }}</span></p></li>
      {% endfor %}
      </ul>
    </details>
  {% endfor %}
  </div>
</section>
{% include contact.html %}
