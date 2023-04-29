package org.altbeacon.beaconreference;


import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.TextStyle;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.TimeZone;

public class HistoryActivity extends Activity {
    private List<String> historyList = new ArrayList<>();
    private ArrayAdapter<String> mAdapter;

    ListView listView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_history);
        historial();

    }

    public void historial(){
        RequestQueue volleyQueue = Volley.newRequestQueue(HistoryActivity.this);
        String url = "https://tfg-u3xd.onrender.com/stays/history";
        JSONObject entrada = new JSONObject();

        try{
            entrada.put("uuid",SplashActivity.getDevId().toString());
        } catch(JSONException e){
            e.printStackTrace();
        }


        MyJsonArrayRequest jsonArrayRequest = new MyJsonArrayRequest(Request.Method.POST,url,entrada
                ,(Response.Listener<JSONArray>) response-> {

            try{
                if(response != null){
                    int len = response.length();
                    Locale spanishLocale=new Locale("es", "ES");
                    for(int cnt = 0; cnt < len; cnt++){

                        JSONObject respuesta = (JSONObject) response.get(cnt);
                        JSONObject date = respuesta.getJSONObject("start_date");
                        String dtAux = (String) date.get("$date");

                        Instant instant = Instant.parse(dtAux);
                        ZonedDateTime time = instant.atZone(ZoneId.of("Europe/Madrid"));

                        String cadena = "";
                        if(respuesta.has("end_date")){
                            JSONObject end_date = respuesta.getJSONObject("end_date");
                            String dtAux2 = (String) end_date.get("$date");
                            Instant instant2 = Instant.parse(dtAux2);
                            ZonedDateTime time2 = instant2.atZone(ZoneId.of("Europe/Madrid"));
                            cadena = cadena + "Habitación: "+ respuesta.getString("room_name") + "\n" +
                                    "Fecha: "+ time.getDayOfWeek().getDisplayName(TextStyle.FULL,spanishLocale) + ", " + time.getDayOfMonth() + "-" + time.getMonth().getDisplayName(TextStyle.FULL,spanishLocale) + "-"+ time.getYear()+ "\n"+
                                    "Hora de entrada: " + time.getHour() + ":" + time.getMinute() + ":" + time.getSecond() + "\n" +
                                    "Hora de salida: " + time2.getHour() + ":" + time2.getMinute() + ":" + time2.getSecond();
                        }
                        else{
                            cadena = cadena + "Habitación: "+ respuesta.getString("room_name") + "\n" +
                                    "Fecha: "+ time.getDayOfWeek().getDisplayName(TextStyle.FULL,spanishLocale) + ", " + time.getDayOfMonth() + "-" + time.getMonth().getDisplayName(TextStyle.FULL,spanishLocale) + "-"+ time.getYear()+ "\n"+
                                    "Hora de entrada: " + time.getHour() + ":" + time.getMinute() + ":" + time.getSecond();
                        }

                        historyList.add(cadena);


                    }
                    listView = (ListView) findViewById(R.id.listaHistorial);
                    mAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, historyList);
                    listView.setAdapter(mAdapter);
                }
            }catch(JSONException e){
                Log.e("MainActivity", "hola");
                e.printStackTrace();
            }
        },
                (Response.ErrorListener) error -> {
                    // make a Toast telling the user
                    // that something went wrong
                    Toast.makeText(HistoryActivity.this, "Se está reactivando el servidor, vuelve a intentarlo en un minuto", Toast.LENGTH_LONG).show();
                    // log the error message in the error stream
                    error.printStackTrace();
                    Log.e("MainActivity", error.toString());
                    Log.e("MainActivity", url);
                    Log.e("MainActivity", entrada.toString());

                });
        volleyQueue.add(jsonArrayRequest);
    }
}