<br> <br>

# Лабораторная работа №1

#### Выполнили:
<div align="left">
  <a href="https://github.com/MrDimaL"><img src="https://img.shields.io/badge/Github-Lopatkin_D.K.-blue"></a> &ensp;
  <a href="https://github.com/BorisTheAnimal"><img src="https://img.shields.io/badge/Github-Berezhnoy_V.A.-green"></a> &ensp;
  <a href="https://github.com/Sukusin"><img src="https://img.shields.io/badge/Github-Sokolov_K.A.-purple"></a> &ensp;
</div>

## Задание:
- Давайте соберем информацию о друзьях и друзьях друзей из VK для членов Вашей группы.
- Оценить центральность: по посредничеству, по близости, собственного вектора (только для членов Вашей группы).
- Дополнительно к центральности в графе необходимо сделать модель прогноза кто с кем дружит (признаки по которым определять дружбу придумайте сами).

> 📁main
> > 📁centrality &emsp; &emsp; &emsp; &emsp; - Расчёты центральностей
> > > 📄centrality.py
> >
> > 📁data &emsp; &emsp; &emsp; &emsp; &emsp; &emsp;- Хранятся данные
> > > 📄friends_features.csv
> > > 📄friends_info.csv
> > > 📄friends_info.json
> > > 📄friends_info_trim.py
> > > 📄friends_map.json
> > > 📄friends_map_trim.py
> > > 📄raw_friends_features.csv
> > > 📄small_friends_info.csv
> > > 📄small_friends_info.json
> > > 📄small_friends_map.json
> >
> > 📁data_creator &emsp; &emsp; &emsp;- Парсинг VKAPI
> > > 📄data_collector.py
> > > 📄friends_info.py
> > > 📄friends_map_creator.py
> > > 📄vk_api.py
> >
> > 📁friend-pred &emsp; &emsp; &emsp; - Работа с признаками и модель
> > > 📄feature_extraction.ipynb
> > > 📄model_train.ipynb
> > > 📄test.ipynb
> > > 📁catboost_info &emsp; - Результаты тренировки
> > > > 📁learn
> > > > > 📄events.out.tfevents
> > > >
> > > > 📁test
> > > > > 📄events.out.tfevents
> > >  >
> > > > 📄catboost_training.json
> > > > 📄learn_error.tsv
> > > > 📄test_error.tsv
> > > > 📄time_left.tsv
> > 
> > 📄main.txt &emsp; &emsp; &emsp; &emsp; &emsp;- Использовался для вызова функций, был тестовым
