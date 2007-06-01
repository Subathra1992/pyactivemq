/*
  Copyright 2007 Albert Strasheim <fullung@gmail.com>

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

#include <boost/python/class.hpp>

#include <cms/TextMessage.h>

namespace py = boost::python;

using cms::TextMessage;
using cms::Message;

void export_TextMessage()
{
    void (TextMessage::*TextMessage_setText)(const std::string&) = &TextMessage::setText;
    py::class_<TextMessage, py::bases<Message>, boost::noncopyable>("TextMessage", py::no_init)
        .add_property("text", &TextMessage::getText, TextMessage_setText)
        ;
}
