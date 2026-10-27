---
title: About & contact
description: Professor Panagiotis Tsoutsanis, Computational Fluid Dynamics, Cranfield University.
---
{% assign profile = site.data.public_profile %}
<header class="page-intro">
  <p class="overline">About & contact</p>
  <h1>{{ profile.display_name | default: site.profile.name | escape }}</h1>
  <p>{{ site.profile.role | escape }}<br>{{ site.profile.institution | escape }}</p>
</header>

<div class="about-grid">
  {% if site.profile.portrait and site.profile.portrait != '' %}
  <img class="about-portrait" src="{{ site.profile.portrait | relative_url | escape }}" alt="Portrait of {{ site.profile.name | escape }}" width="320" height="320">
  {% endif %}
  <div>
    <div class="prose">
      {% for paragraph in profile.biography %}<p>{{ paragraph | escape }}</p>{% endfor %}
      <p><a href="{{ '/research/' | relative_url }}">Research overview and areas of expertise →</a></p>
    </div>
    <div class="actions">
      <a class="button button-primary" href="mailto:{{ site.profile.email | escape }}" data-goatcounter-click="contact-email">Email me ↗</a>
      {% if site.profile.cv and site.profile.cv != '' %}<a class="button" href="{{ site.profile.cv | relative_url | escape }}" data-goatcounter-click="download-cv">Download CV · PDF</a>{% endif %}
      {% if site.profile.institutional_url and site.profile.institutional_url != '' %}<a class="button" href="{{ site.profile.institutional_url | escape }}" target="_blank" rel="noopener noreferrer">Institutional profile ↗</a>{% endif %}
    </div>
    <div class="profile-links">
      {% if site.profile.orcid and site.profile.orcid != '' %}<a href="{{ site.profile.orcid | escape }}" target="_blank" rel="noopener noreferrer">ORCID</a>{% endif %}
      {% if site.profile.scholar and site.profile.scholar != '' %}<a href="{{ site.profile.scholar | escape }}" target="_blank" rel="noopener noreferrer">Google Scholar</a>{% endif %}
      {% if site.github_username and site.github_username != '' %}<a href="https://github.com/{{ site.github_username | escape }}" target="_blank" rel="noopener noreferrer">GitHub</a>{% endif %}
    </div>
  </div>
</div>

{% if profile.education.size > 0 %}
<section class="section" aria-labelledby="education-heading">
  <div class="section-heading"><div><p class="overline">Background</p><h2 id="education-heading">Education</h2></div></div>
  <ol class="profile-timeline">
    {% for item in profile.education %}
    <li>
      <p class="overline">{{ item.years | escape }}</p>
      <div><h3>{{ item.qualification | escape }}</h3><p>{{ item.institution | escape }}</p>{% if item.thesis and item.thesis != '' %}<p class="quiet">Thesis: {{ item.thesis | escape }}</p>{% endif %}</div>
    </li>
    {% endfor %}
  </ol>
</section>
{% endif %}

{% if profile.distinctions.size > 0 %}
<section class="section" aria-labelledby="distinctions-heading">
  <div class="section-heading"><div><p class="overline">Recognition</p><h2 id="distinctions-heading">Selected distinctions</h2></div></div>
  <ul class="detail-list">
    {% for item in profile.distinctions %}
    <li>
      <p class="overline">{{ item.year | escape }}</p>
      <h3>{{ item.title | escape }}</h3>
      {% if item.work and item.work != '' %}<p>{{ item.work | escape }}</p>{% endif %}
      {% if item.url and item.url != '' %}<a class="text-link" href="{{ item.url | escape }}" target="_blank" rel="noopener noreferrer">Award record ↗</a>{% endif %}
    </li>
    {% endfor %}
  </ul>
</section>
{% endif %}
